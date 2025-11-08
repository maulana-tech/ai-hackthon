import asyncio
import logging
from typing import List, Dict, Any, Optional
import re
import httpx

from app.models.schemas import Supplier
from app.integrations.firecrawl_client import FirecrawlClient
from app.integrations.apify_client import ApifyIntegration
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class SupplierScoutAgent:
    """Agent to find suppliers in Indonesian marketplaces"""
    
    def __init__(self):
        self.firecrawl = FirecrawlClient()
        self.apify = ApifyIntegration()
        self.name = "Supplier Scout Agent"
        self.use_apify = True  # Flag to enable/disable Apify
        
    async def find_suppliers(
        self,
        product_name: str,
        location: Optional[str] = None,
        min_rating: float = 4.0,
        limit: int = 5,
        use_apify: Optional[bool] = None
    ) -> List[Supplier]:
        """
        Main method to find suppliers from multiple marketplaces
        
        Args:
            product_name: Product to search
            location: Optional location filter
            min_rating: Minimum supplier rating
            limit: Maximum suppliers to return
            use_apify: Use Apify (faster) or Firecrawl (more flexible)
            
        Returns:
            List of ranked suppliers
        """
        logger.info(f"Starting supplier search for: {product_name}")
        
        # Determine which scraping method to use
        use_apify_flag = use_apify if use_apify is not None else self.use_apify
        
        if use_apify_flag:
            # Use Apify for faster, more reliable scraping
            logger.info("Using Apify for marketplace scraping")
            all_suppliers = await self._search_with_apify(product_name, min_rating, limit)
        else:
            # Use Firecrawl for custom sites
            logger.info("Using Firecrawl for marketplace scraping")
            all_suppliers = await self._search_with_firecrawl(product_name, min_rating)
        
        # Filter by location if specified
        if location:
            all_suppliers = [s for s in all_suppliers if location.lower() in s.location.lower()]
            
        # Rank and filter
        ranked_suppliers = self._rank_and_filter(all_suppliers, limit)
        
        return ranked_suppliers
    
    async def _search_with_apify(
        self,
        product_name: str,
        min_rating: float,
        limit: int
    ) -> List[Supplier]:
        """Search using Apify (faster, more reliable)"""
        try:
            # Scrape marketplaces in parallel with Apify
            suppliers = await self.apify.get_suppliers_from_all_marketplaces(
                product_name=product_name,
                max_suppliers=limit * 3,  # Get more for filtering
                min_rating=min_rating
            )
            
            # Also search Indonetwork with Firecrawl (B2B specific)
            indonetwork_suppliers = await self._search_indonetwork(product_name, min_rating)
            
            # Combine results
            all_suppliers = suppliers + indonetwork_suppliers
            
            logger.info(f"Found {len(all_suppliers)} suppliers via Apify + Firecrawl")
            return all_suppliers
            
        except Exception as e:
            logger.error(f"Apify search error: {str(e)}")
            # Fallback to Firecrawl
            return await self._search_with_firecrawl(product_name, min_rating)
    
    async def _search_with_firecrawl(
        self,
        product_name: str,
        min_rating: float
    ) -> List[Supplier]:
        """Search using Firecrawl (fallback method)"""
        try:
            tasks = [
                self._search_indonetwork(product_name, min_rating),
                self._search_tokopedia(product_name, min_rating),
                self._search_shopee(product_name, min_rating),
                self._search_lazada(product_name, min_rating)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_suppliers = []
            for result in results:
                if isinstance(result, list):
                    all_suppliers.extend(result)
                elif isinstance(result, Exception):
                    logger.warning(f"Task failed: {str(result)}")
            
            logger.info(f"Found {len(all_suppliers)} suppliers via Firecrawl")
            return all_suppliers
            
        except Exception as e:
            logger.error(f"Firecrawl search error: {str(e)}")
            return []
        
    async def _search_indonetwork(self, product_name: str, min_rating: float) -> List[Supplier]:
        """Search Indonetwork.co.id for B2B suppliers with full contact details"""
        try:
            logger.info(f"Searching Indonetwork for: {product_name}")
            
            search_url = f"https://www.indonetwork.co.id/search?q={product_name.replace(' ', '+')}"
            
            actions = [
                {"type": "wait", "milliseconds": 3000},
                {"type": "scroll", "y": 1500},
                {"type": "wait", "milliseconds": 1500}
            ]
            
            result = await self.firecrawl.scrape_with_actions(
                search_url,
                actions=actions,
                formats=[{
                    "type": "json",
                    "prompt": """Extract list of companies/suppliers with:
                    - company_name
                    - product_name
                    - company_url (full URL to company page)
                    - location/city
                    - contact_person
                    - phone
                    - email
                    - address
                    - product_description
                    - minimum_order_quantity"""
                }]
            )
            
            suppliers = []
            
            if result and 'data' in result:
                data = result['data']
                if 'json' in data:
                    json_data = data['json']
                    
                    companies_list = []
                    if isinstance(json_data, dict):
                        if 'companies' in json_data:
                            companies_list = json_data['companies']
                        elif 'suppliers' in json_data:
                            companies_list = json_data['suppliers']
                        elif 'results' in json_data:
                            companies_list = json_data['results']
                            
                    for company in companies_list[:5]:
                        company_url = company.get('company_url', '')
                        
                        if company_url and company_url.startswith('http'):
                            detailed_info = await self._get_indonetwork_company_details(company_url)
                            if detailed_info:
                                company.update(detailed_info)
                        
                        supplier = Supplier(
                            name=company.get('company_name', 'Indonetwork Supplier'),
                            store_name=company.get('company_name', 'Unknown Company'),
                            rating=4.5,
                            location=company.get('address', company.get('location', 'Indonesia')),
                            city=self._extract_city(company.get('location', company.get('city', 'Jakarta'))),
                            product_name=company.get('product_name', product_name),
                            price=float(company.get('price', 0)) if company.get('price') else 0.0,
                            currency="IDR",
                            stock_available=True,
                            minimum_order=int(company.get('minimum_order_quantity', company.get('moq', 1))),
                            url=company_url or search_url,
                            phone=company.get('phone', company.get('telephone', '')),
                            email=company.get('email', ''),
                            marketplace="Indonetwork",
                            verified=True,
                            response_rate=80.0
                        )
                        suppliers.append(supplier)
                        
            logger.info(f"Found {len(suppliers)} suppliers on Indonetwork")
            return suppliers
            
        except Exception as e:
            logger.error(f"Error searching Indonetwork: {str(e)}")
            return []
    
    async def _get_indonetwork_company_details(self, company_url: str) -> Dict[str, Any]:
        """Get detailed company information from Indonetwork company page"""
        try:
            logger.info(f"Fetching company details: {company_url}")
            
            actions = [
                {"type": "wait", "milliseconds": 2000},
                {"type": "scroll", "y": 1000},
                {"type": "wait", "milliseconds": 1000}
            ]
            
            result = await self.firecrawl.scrape_with_actions(
                company_url,
                actions=actions,
                formats=[{
                    "type": "json",
                    "prompt": """Extract complete company information:
                    - company_name
                    - contact_person
                    - phone (all phone numbers)
                    - mobile
                    - email
                    - website
                    - address (complete address)
                    - city
                    - province
                    - postal_code
                    - products (list of products they offer)
                    - business_type
                    - year_established
                    - employee_count
                    - main_products
                    - description"""
                }]
            )
            
            if result and 'data' in result and 'json' in result['data']:
                return result['data']['json']
            
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching company details: {str(e)}")
            return {}
    
    async def batch_scrape_companies(self, company_urls: List[str]) -> List[Dict[str, Any]]:
        """Batch scrape multiple company URLs from Indonetwork"""
        logger.info(f"Batch scraping {len(company_urls)} company pages")
        
        tasks = [
            self._get_indonetwork_company_details(url)
            for url in company_urls
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        companies = []
        for result in results:
            if isinstance(result, dict) and result:
                companies.append(result)
            elif isinstance(result, Exception):
                logger.warning(f"Company scrape failed: {str(result)}")
        
        logger.info(f"Successfully scraped {len(companies)} companies")
        return companies
    
    async def _search_tokopedia(self, product_name: str, min_rating: float) -> List[Supplier]:
        """Search Tokopedia for suppliers"""
        try:
            logger.info(f"Searching Tokopedia for: {product_name}")
            
            search_url = f"https://www.tokopedia.com/search?q={product_name.replace(' ', '%20')}"
            
            actions = [
                {"type": "wait", "milliseconds": 2000},
                {"type": "scroll", "y": 1000},
                {"type": "wait", "milliseconds": 1000}
            ]
            
            result = await self.firecrawl.scrape_with_actions(
                search_url,
                actions=actions,
                formats=[{
                    "type": "json",
                    "prompt": "Extract: store name, product name, price, rating, location, stock status, seller info"
                }]
            )
            
            suppliers = []
            
            if result and 'data' in result:
                data = result['data']
                if 'json' in data:
                    json_data = data['json']
                    
                    products_list = []
                    if isinstance(json_data, dict):
                        if 'products' in json_data:
                            products_list = json_data['products']
                        elif 'items' in json_data:
                            products_list = json_data['items']
                            
                    for item in products_list[:3]:
                        rating = float(item.get('rating', 4.5))
                        if rating >= min_rating:
                            price_str = str(item.get('price', '0'))
                            price = float(re.sub(r'[^\d.]', '', price_str.replace('Rp', '').replace('.', '').replace(',', '.')))
                            
                            supplier = Supplier(
                                name=item.get('seller_name', item.get('store_name', 'Tokopedia Seller')),
                                store_name=item.get('store_name', 'Unknown Store'),
                                rating=rating,
                                location=item.get('location', 'Indonesia'),
                                city=item.get('city', self._extract_city(item.get('location', ''))),
                                product_name=item.get('product_name', product_name),
                                price=price,
                                currency="IDR",
                                stock_available=item.get('stock', 'available').lower() != 'habis',
                                minimum_order=int(item.get('min_order', 1)),
                                url=item.get('url', search_url),
                                marketplace="Tokopedia",
                                verified=item.get('verified', False),
                                response_rate=item.get('response_rate', 85.0)
                            )
                            suppliers.append(supplier)
                            
            return suppliers
            
        except Exception as e:
            logger.error(f"Error searching Tokopedia: {str(e)}")
            return []
            
    async def _search_shopee(self, product_name: str, min_rating: float) -> List[Supplier]:
        """Search Shopee for suppliers"""
        try:
            logger.info(f"Searching Shopee for: {product_name}")
            
            search_url = f"https://shopee.co.id/search?keyword={product_name.replace(' ', '%20')}"
            
            actions = [
                {"type": "wait", "milliseconds": 2500},
                {"type": "scroll", "y": 1000},
                {"type": "wait", "milliseconds": 1000}
            ]
            
            result = await self.firecrawl.scrape_with_actions(
                search_url,
                actions=actions,
                formats=[{
                    "type": "json",
                    "prompt": "Extract: shop name, product name, price, rating, location, stock, minimum order"
                }]
            )
            
            suppliers = []
            
            if result and 'data' in result:
                data = result['data']
                if 'json' in data:
                    json_data = data['json']
                    
                    products_list = []
                    if isinstance(json_data, dict):
                        if 'products' in json_data:
                            products_list = json_data['products']
                        elif 'items' in json_data:
                            products_list = json_data['items']
                            
                    for item in products_list[:3]:
                        rating = float(item.get('rating', 4.5))
                        if rating >= min_rating:
                            price_str = str(item.get('price', '0'))
                            price = float(re.sub(r'[^\d.]', '', price_str.replace('Rp', '').replace('.', '').replace(',', '.')))
                            
                            supplier = Supplier(
                                name=item.get('shop_name', 'Shopee Seller'),
                                store_name=item.get('shop_name', 'Unknown Store'),
                                rating=rating,
                                location=item.get('shop_location', 'Indonesia'),
                                city=item.get('city', self._extract_city(item.get('shop_location', ''))),
                                product_name=item.get('name', product_name),
                                price=price,
                                currency="IDR",
                                stock_available=int(item.get('stock', 10)) > 0,
                                minimum_order=int(item.get('min_order', 1)),
                                url=item.get('url', search_url),
                                marketplace="Shopee",
                                verified=item.get('is_official_shop', False),
                                response_rate=item.get('response_rate', 90.0)
                            )
                            suppliers.append(supplier)
                            
            return suppliers
            
        except Exception as e:
            logger.error(f"Error searching Shopee: {str(e)}")
            return []
            
    async def _search_lazada(self, product_name: str, min_rating: float) -> List[Supplier]:
        """Search Lazada using RapidAPI"""
        try:
            logger.info(f"Searching Lazada for: {product_name}")
            
            url = f"https://{settings.lazada_api_host}/search"
            
            headers = {
                "X-RapidAPI-Key": settings.rapidapi_key,
                "X-RapidAPI-Host": settings.lazada_api_host
            }
            
            params = {
                "q": product_name,
                "country": "id"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    suppliers = []
                    items = data.get('items', [])[:3]
                    
                    for item in items:
                        rating = float(item.get('rating', 4.5))
                        if rating >= min_rating:
                            supplier = Supplier(
                                name=item.get('seller_name', 'Lazada Seller'),
                                store_name=item.get('shop_name', 'Unknown Store'),
                                rating=rating,
                                location=item.get('location', 'Indonesia'),
                                city=item.get('city', 'Jakarta'),
                                product_name=item.get('title', product_name),
                                price=float(item.get('price', 0)),
                                currency="IDR",
                                stock_available=True,
                                minimum_order=1,
                                url=item.get('url', ''),
                                marketplace="Lazada",
                                verified=item.get('is_official', False),
                                response_rate=85.0
                            )
                            suppliers.append(supplier)
                            
                    return suppliers
                else:
                    logger.warning(f"Lazada API returned status {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching Lazada: {str(e)}")
            return []
            
    def _rank_and_filter(self, suppliers: List[Supplier], limit: int) -> List[Supplier]:
        """Rank suppliers by rating and response rate"""
        
        for supplier in suppliers:
            supplier_score = (
                supplier.rating * 0.6 +
                (supplier.response_rate or 0) / 100 * 0.3 +
                (0.1 if supplier.verified else 0) * 10
            )
            
        sorted_suppliers = sorted(
            suppliers,
            key=lambda x: (x.rating, x.response_rate or 0),
            reverse=True
        )
        
        return sorted_suppliers[:limit]
        
    def _extract_city(self, location: str) -> str:
        """Extract city name from location string"""
        major_cities = [
            'Jakarta', 'Surabaya', 'Bandung', 'Medan', 'Semarang',
            'Makassar', 'Palembang', 'Tangerang', 'Depok', 'Bekasi',
            'Bogor', 'Yogyakarta', 'Malang', 'Bali', 'Denpasar'
        ]
        
        for city in major_cities:
            if city.lower() in location.lower():
                return city
                
        return location.split(',')[0] if ',' in location else location
        
    async def search_indonetwork_by_category(self, category: str, limit: int = 10) -> List[Supplier]:
        """Search Indonetwork by product category"""
        try:
            logger.info(f"Searching Indonetwork by category: {category}")
            
            category_url = f"https://www.indonetwork.co.id/category/{category.lower().replace(' ', '-')}"
            
            result = await self.firecrawl.crawl(
                category_url,
                limit=limit,
                formats=["json"]
            )
            
            suppliers = []
            
            if isinstance(result, list):
                for page in result:
                    if 'data' in page and 'json' in page['data']:
                        json_data = page['data']['json']
                        
                        if isinstance(json_data, dict) and 'companies' in json_data:
                            for company in json_data['companies']:
                                supplier = Supplier(
                                    name=company.get('name', 'Unknown'),
                                    store_name=company.get('name', 'Unknown'),
                                    rating=4.5,
                                    location=company.get('location', 'Indonesia'),
                                    city=self._extract_city(company.get('location', 'Jakarta')),
                                    product_name=category,
                                    price=0.0,
                                    currency="IDR",
                                    stock_available=True,
                                    minimum_order=1,
                                    url=company.get('url', ''),
                                    phone=company.get('phone', ''),
                                    email=company.get('email', ''),
                                    marketplace="Indonetwork",
                                    verified=True,
                                    response_rate=80.0
                                )
                                suppliers.append(supplier)
            
            return suppliers[:limit]
            
        except Exception as e:
            logger.error(f"Error searching Indonetwork by category: {str(e)}")
            return []
    
    async def get_indonetwork_supplier_with_markdown(self, company_url: str) -> Dict[str, Any]:
        """Get supplier info with markdown format (for documentation/reports)"""
        try:
            logger.info(f"Getting supplier info with markdown: {company_url}")
            
            result = await self.firecrawl.scrape(
                company_url,
                formats=["markdown", {
                    "type": "json",
                    "prompt": "Extract all company and contact information"
                }]
            )
            
            return {
                "markdown": result.get('data', {}).get('markdown', ''),
                "structured_data": result.get('data', {}).get('json', {}),
                "metadata": result.get('data', {}).get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Error getting markdown supplier info: {str(e)}")
            return {}
    
    async def generate_search_summary(self, suppliers: List[Supplier]) -> str:
        """Generate a summary of supplier search"""
        if not suppliers:
            return "No suppliers found for your query."
            
        summary = f"Found {len(suppliers)} verified suppliers:\n\n"
        
        for i, supplier in enumerate(suppliers, 1):
            summary += f"{i}. **{supplier.store_name}** ({supplier.marketplace})\n"
            summary += f"   - Location: {supplier.city}\n"
            
            if supplier.marketplace == "Indonetwork":
                if supplier.phone:
                    summary += f"   - Phone: {supplier.phone}\n"
                if supplier.email:
                    summary += f"   - Email: {supplier.email}\n"
            else:
                summary += f"   - Rating: {supplier.rating}/5.0\n"
                summary += f"   - Price: Rp {supplier.price:,.0f}\n"
            
            summary += f"   - Min Order: {supplier.minimum_order} pcs\n"
            summary += f"   - Stock: {'✓ Available' if supplier.stock_available else '✗ Out of Stock'}\n"
            
            if supplier.url:
                summary += f"   - URL: {supplier.url}\n"
            
            summary += "\n"
            
        return summary
