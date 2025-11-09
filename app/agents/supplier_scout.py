import asyncio
import logging
from typing import List, Dict, Any, Optional
import re
import httpx
import json
from pathlib import Path

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
        
        Priority:
        1. Load from sample_shopee_data.json (instant, no API calls)
        2. If not found, load from data/suppliers/ folder
        
        Args:
            product_name: Product to search
            location: Optional location filter
            min_rating: Minimum supplier rating
            limit: Maximum suppliers to return
            use_apify: Ignored (kept for backward compatibility)
            
        Returns:
            List of ranked suppliers
        """
        logger.info(f"Loading supplier data for: {product_name}")
        
        all_suppliers = []
        
        # PRIORITY 1: Load from sample_shopee_data.json (instant, no scraping)
        logger.info("📂 Loading suppliers from sample_shopee_data.json...")
        all_suppliers = await self._load_sample_shopee_data(product_name, min_rating, limit)
        
        # PRIORITY 2: If not found, load from data/suppliers/ folder
        if not all_suppliers or len(all_suppliers) == 0:
            logger.info(f"No suppliers in sample data, trying data/suppliers/ folder...")
            all_suppliers = await self._load_fallback_supplier_data(product_name, min_rating, limit)
        
        # Filter by location if specified
        if location:
            all_suppliers = [s for s in all_suppliers if location.lower() in s.location.lower()]
            
        # Rank and filter
        ranked_suppliers = self._rank_and_filter(all_suppliers, limit)
        
        logger.info(f"✅ Returning {len(ranked_suppliers)} suppliers for {product_name}")
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
            
            # First, get search results page
            result = await self.firecrawl.scrape(
                search_url,
                formats=["markdown", "html"]
            )
            
            if not result or 'linksOnPage' not in result:
                logger.warning("No links found in search results")
                return []
            
            # Extract product links
            product_links = [
                link for link in result.get('linksOnPage', [])
                if '/product/' in link and 'indonetwork.co.id' in link
            ]
            
            logger.info(f"Found {len(product_links)} product links")
            
            if not product_links:
                return []
            
            # Scrape first 5 product pages for details
            suppliers = []
            for product_url in product_links[:5]:
                try:
                    logger.info(f"Scraping product: {product_url}")
                    
                    # Scrape individual product page with AI extraction
                    product_result = await self.firecrawl.scrape(
                        product_url,
                        formats=["markdown"]
                    )
                    
                    if product_result and 'markdown' in product_result:
                        markdown = product_result['markdown']
                        
                        # Parse supplier info from markdown
                        supplier = self._parse_indonetwork_product(markdown, product_url)
                        if supplier and supplier.rating >= min_rating:
                            suppliers.append(supplier)
                    
                    # Small delay between requests
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error scraping product {product_url}: {str(e)}")
                    continue
            
            logger.info(f"Successfully scraped {len(suppliers)} suppliers from Indonetwork")
            return suppliers
            
        except Exception as e:
            logger.error(f"Error searching Indonetwork: {str(e)}")
            return []
    
    def _parse_indonetwork_product(self, markdown: str, product_url: str) -> Optional[Supplier]:
        """Parse Indonetwork product page markdown to extract supplier info"""
        try:
            import re
            
            # Extract company name - look for "### CV." or "### PT." pattern
            # This is the actual company heading in the markdown
            company_match = re.search(r'###\s+((?:CV\.|PT\.|UD\.|Toko\s)\s*[^\n]+)', markdown, re.IGNORECASE)
            if not company_match:
                # Alternative: look for company section link pattern
                company_match = re.search(r'### \[([^\]]+)\]\(https://www\.indonetwork\.co\.id/company/', markdown)
            
            company_name = company_match.group(1).strip() if company_match else "Unknown Supplier"
            
            # Extract product name - look for the H1 heading (# heading)
            product_match = re.search(r'^# (.+)$', markdown, re.MULTILINE)
            if not product_match:
                # Fallback: look for product in breadcrumb or title
                product_match = re.search(r'- (Botol [^\n]+|Pot [^\n]+|\w+ [^\n]+)\n', markdown)
            
            product_name = product_match.group(1).strip() if product_match else "Product"
            
            # Extract full address - look for complete address pattern after company info
            address_match = re.search(r'(?:Perumahan|Jalan|Jl\.|Gedung|Kompleks)\s+([^\n]+)\n([^\n]+?(?:Jakarta|Surabaya|Bandung|Semarang|Yogyakarta|Bali|Gresik|Tangerang|Bekasi|Bogor|Depok|Malang|Medan)[^\n]*)', markdown, re.IGNORECASE | re.DOTALL)
            if address_match:
                location = f"{address_match.group(1).strip()}, {address_match.group(2).strip()}"
            else:
                # Fallback to simpler pattern
                location_match = re.search(r'([^\n]*(?:Jakarta|Surabaya|Bandung|Semarang|Yogyakarta|Bali|Gresik|Tangerang|Bekasi|Bogor|Depok|Malang|Medan)[^\n]*)', markdown, re.IGNORECASE)
                location = location_match.group(1).strip() if location_match else "Indonesia"
            
            # Extract WhatsApp - look for the specific pattern "WHATSAPP : 0822-2424-9969"
            whatsapp_match = re.search(r'(?:WHATSAPP|WhatsApp|WA)\s*[:：]\s*([\d\-\+\(\)\s]+)', markdown, re.IGNORECASE)
            whatsapp = ""
            if whatsapp_match:
                # Clean up the number
                whatsapp = whatsapp_match.group(1).strip()
            else:
                # Fallback 1: look for Indonesian phone number format in CONTACT section
                contact_section = re.search(r'CONTACT[^\n]*\n([^\n]*\n){0,5}', markdown, re.IGNORECASE)
                if contact_section:
                    contact_text = contact_section.group(0)
                    whatsapp_match = re.search(r'(0\d{3,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4})', contact_text)
                    if whatsapp_match:
                        whatsapp = whatsapp_match.group(1).strip()
                
                # Fallback 2: look anywhere in markdown for Indonesian phone
                if not whatsapp:
                    # Look for pattern near phone-related keywords
                    phone_context = re.search(r'(?:hubungi|contact|telp|hp|call|phone)[^\n]{0,30}(0\d{3,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4})', markdown, re.IGNORECASE)
                    if phone_context:
                        whatsapp = phone_context.group(1).strip()
            
            # Extract phone (same logic as WhatsApp for now)
            phone_match = re.search(r'(?:TELEPON|Telp|Phone|HP)\s*[:：]\s*([\d\-\+\(\)\s]+)', markdown, re.IGNORECASE)
            phone = ""
            if phone_match:
                phone = phone_match.group(1).strip()
            else:
                # Use WhatsApp as fallback
                phone = whatsapp
            
            # Extract email (comprehensive pattern)
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', markdown)
            email = email_match.group(1).strip() if email_match else ""
            
            # Extract price (Rp, IDR)
            price_match = re.search(r'(?:Rp|IDR)[.\s]*([0-9.,]+)', markdown, re.IGNORECASE)
            price = 0
            if price_match:
                price_str = price_match.group(1).replace('.', '').replace(',', '')
                try:
                    price = int(price_str)
                except:
                    price = 0
            
            # Extract MOQ - look for "Minimum Pembelian" section
            moq_match = re.search(r'Minimum Pembelian\s*\n\s*(\d+)', markdown, re.IGNORECASE)
            if not moq_match:
                moq_match = re.search(r'(?:MOQ|Minimum Order|Min\. Order)[:\s]*([0-9]+)', markdown, re.IGNORECASE)
            moq = int(moq_match.group(1)) if moq_match else 1
            
            # Extract city from location - prioritize major cities
            major_cities = ['Jakarta', 'Surabaya', 'Bandung', 'Semarang', 'Yogyakarta', 'Bali', 'Gresik', 'Tangerang', 'Bekasi', 'Bogor', 'Depok', 'Malang', 'Medan']
            city = "Indonesia"
            for c in major_cities:
                if c.lower() in location.lower():
                    city = c
                    break
            
            # Create supplier object
            supplier = Supplier(
                name=company_name,
                store_name=company_name,
                marketplace="Indonetwork",
                location=location,
                city=city,
                rating=4.5,  # Default rating for Indonetwork (B2B verified)
                product_name=product_name,
                price=price,
                currency="IDR",
                minimum_order=moq,
                stock_available=True,
                phone=phone,
                email=email,
                whatsapp=whatsapp,
                url=product_url,
                verified=True,
                response_rate=85.0,
                is_bestseller=True,  # B2B suppliers are typically reliable
                total_sold=None,
                review_count=None
            )
            
            logger.info(f"Parsed supplier: {company_name} - {product_name}")
            return supplier
            
        except Exception as e:
            logger.error(f"Error parsing Indonetwork product: {str(e)}")
            return None
    
    async def _OLD_search_indonetwork_DEPRECATED(self, product_name: str, min_rating: float) -> List[Supplier]:
        """OLD METHOD - DEPRECATED - kept for reference only"""
        try:
            suppliers = []
            
            if False and result and 'data' in result:
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
        """Search Tokopedia for suppliers (BESTSELLERS ONLY)"""
        try:
            logger.info(f"Searching Tokopedia for: {product_name}")
            
            # Add sort by bestseller parameter
            search_url = f"https://www.tokopedia.com/search?q={product_name.replace(' ', '%20')}&ob=5"
            
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
                    "prompt": """Extract ONLY from top/bestselling products (highest sold):
                    - store name
                    - seller name
                    - product name
                    - price
                    - rating
                    - location
                    - stock status
                    - total sold (terjual)
                    - review count
                    - seller phone/whatsapp (if visible)
                    - seller email (if visible)
                    - is bestseller badge present
                    Focus on products with highest sales numbers."""
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
                            
                            # Extract contact information
                            phone = item.get('phone', item.get('whatsapp', ''))
                            email = item.get('email', '')
                            
                            # Extract sales metrics
                            total_sold = item.get('total_sold', item.get('sold', item.get('terjual', 0)))
                            if isinstance(total_sold, str):
                                total_sold = int(re.sub(r'[^\d]', '', total_sold)) if total_sold else 0
                            
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
                                phone=phone,
                                email=email,
                                whatsapp=item.get('whatsapp', phone),
                                marketplace="Tokopedia",
                                verified=item.get('verified', False),
                                response_rate=item.get('response_rate', 85.0),
                                is_bestseller=item.get('is_bestseller', False) or total_sold > 100,
                                total_sold=total_sold,
                                review_count=item.get('review_count', 0)
                            )
                            suppliers.append(supplier)
                            
            return suppliers
            
        except Exception as e:
            logger.error(f"Error searching Tokopedia: {str(e)}")
            return []
            
    async def _search_shopee(self, product_name: str, min_rating: float) -> List[Supplier]:
        """Search Shopee for suppliers (BESTSELLERS ONLY)"""
        try:
            logger.info(f"Searching Shopee for: {product_name}")
            
            # Add sort by sales parameter (sortBy=sales)
            search_url = f"https://shopee.co.id/search?keyword={product_name.replace(' ', '%20')}&sortBy=sales"
            
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
                    "prompt": """Extract ONLY from top-selling products (sorted by sales):
                    - shop name
                    - seller name
                    - product name
                    - price
                    - rating
                    - location/city
                    - stock status
                    - total sold (terjual)
                    - review count
                    - minimum order
                    - shop phone/whatsapp (if visible)
                    - shop email (if visible)
                    - is official shop or mall badge
                    Focus on products with highest sold count."""
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
                            
                            # Extract contact information
                            phone = item.get('phone', item.get('shop_phone', item.get('whatsapp', '')))
                            email = item.get('email', item.get('shop_email', ''))
                            
                            # Extract sales metrics
                            total_sold = item.get('total_sold', item.get('sold', item.get('terjual', 0)))
                            if isinstance(total_sold, str):
                                total_sold = int(re.sub(r'[^\d]', '', total_sold)) if total_sold else 0
                            
                            supplier = Supplier(
                                name=item.get('shop_name', 'Shopee Seller'),
                                store_name=item.get('shop_name', 'Unknown Store'),
                                rating=rating,
                                location=item.get('shop_location', item.get('location', 'Indonesia')),
                                city=item.get('city', self._extract_city(item.get('shop_location', item.get('location', '')))),
                                product_name=item.get('name', item.get('product_name', product_name)),
                                price=price,
                                currency="IDR",
                                stock_available=int(item.get('stock', 10)) > 0,
                                minimum_order=int(item.get('min_order', 1)),
                                url=item.get('url', search_url),
                                phone=phone,
                                email=email,
                                whatsapp=item.get('whatsapp', phone),
                                marketplace="Shopee",
                                verified=item.get('is_official_shop', item.get('is_mall', False)),
                                response_rate=item.get('response_rate', 90.0),
                                is_bestseller=item.get('is_official_shop', False) or total_sold > 100,
                                total_sold=total_sold,
                                review_count=item.get('review_count', 0)
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
            
    async def _load_sample_shopee_data(
        self,
        product_name: str,
        min_rating: float,
        limit: int
    ) -> List[Supplier]:
        """
        Load supplier data from data/sample_shopee_data.json
        
        This file contains pre-scraped Shopee supplier data with email contacts.
        """
        try:
            logger.info(f"Loading from sample_shopee_data.json for: {product_name}")
            
            sample_file = Path("data/sample_shopee_data.json")
            if not sample_file.exists():
                logger.warning(f"sample_shopee_data.json not found")
                return []
            
            # Load JSON
            with open(sample_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                logger.warning("sample_shopee_data.json is not an array")
                return []
            
            logger.info(f"Found {len(data)} suppliers in sample data")
            
            suppliers = []
            product_lower = product_name.lower()
            
            # Parse each supplier
            for item in data:
                try:
                    # Check if product matches (search in title, description, keyword)
                    title = item.get('title', '').lower()
                    description = item.get('description', '').lower()
                    keyword = item.get('keyword', '').lower()
                    
                    # Simple keyword matching
                    if not any(word in title or word in description or word in keyword 
                              for word in product_lower.split()):
                        continue
                    
                    # Create Supplier object
                    supplier = Supplier(
                        name=item.get('title', 'Unknown'),
                        store_name=item.get('title', 'Unknown'),
                        rating=4.5,  # Default good rating for suppliers with email
                        location='Indonesia',
                        city='Indonesia',
                        product_name=item.get('title', product_name),
                        price=100000,  # Default reasonable price
                        currency='IDR',
                        stock_available=True,
                        minimum_order=1,
                        url=item.get('url', ''),
                        phone='',
                        email=item.get('email', ''),
                        whatsapp='',
                        marketplace='Shopee',
                        response_rate=85.0,
                        verified=True
                    )
                    
                    # Filter by rating
                    if supplier.rating >= min_rating:
                        suppliers.append(supplier)
                    
                    # Stop if we have enough
                    if len(suppliers) >= limit * 2:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error parsing supplier: {str(e)}")
                    continue
            
            logger.info(f"✅ Loaded {len(suppliers)} matching suppliers from sample data")
            return suppliers[:limit * 2]  # Return extra for ranking
            
        except Exception as e:
            logger.error(f"Error loading sample_shopee_data.json: {str(e)}")
            return []
    
    async def _load_fallback_supplier_data(
        self,
        product_name: str,
        min_rating: float,
        limit: int
    ) -> List[Supplier]:
        """
        Load pre-scraped supplier data from data/suppliers/ folder
        
        This is used as fallback when Apify/Firecrawl scraping fails or is rate limited.
        """
        try:
            logger.info(f"Loading fallback supplier data for: {product_name}")
            
            data_folder = Path("data/suppliers")
            if not data_folder.exists():
                logger.warning(f"Supplier data folder does not exist: {data_folder}")
                return []
            
            suppliers = []
            
            # Normalize product name for matching
            product_lower = product_name.lower()
            
            # Read all JSON files in data/suppliers/
            for json_file in data_folder.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Check if this file matches the product
                    file_product = data.get('product', '').lower()
                    
                    # Match if product name is in filename or in data
                    if product_lower in json_file.stem.lower() or product_lower in file_product:
                        logger.info(f"✅ Found matching supplier data: {json_file.name}")
                        
                        # Parse suppliers from JSON
                        supplier_list = data.get('suppliers', [])
                        
                        for supplier_data in supplier_list:
                            try:
                                # Create Supplier object with fallback values
                                supplier = Supplier(
                                    name=supplier_data.get('name', supplier_data.get('store_name', 'Unknown')),
                                    store_name=supplier_data.get('store_name', supplier_data.get('name', 'Unknown')),
                                    rating=float(supplier_data.get('rating', 4.5)),
                                    location=supplier_data.get('location', 'Indonesia'),
                                    city=supplier_data.get('city', supplier_data.get('location', '').split(',')[0] if ',' in supplier_data.get('location', '') else supplier_data.get('location', 'Indonesia')),
                                    product_name=supplier_data.get('product_name', product_name),
                                    price=float(supplier_data.get('price', 0)),
                                    currency=supplier_data.get('currency', 'IDR'),
                                    stock_available=supplier_data.get('stock_available', True),
                                    minimum_order=int(supplier_data.get('minimum_order', 1)),
                                    url=supplier_data.get('url', ''),
                                    phone=supplier_data.get('phone', ''),
                                    email=supplier_data.get('email', ''),
                                    whatsapp=supplier_data.get('whatsapp', ''),
                                    marketplace=supplier_data.get('marketplace', 'Indonetwork'),
                                    response_rate=supplier_data.get('response_rate'),
                                    verified=supplier_data.get('verified', False)
                                )
                                
                                # Filter by rating
                                if supplier.rating >= min_rating:
                                    suppliers.append(supplier)
                                
                            except Exception as e:
                                logger.warning(f"Error parsing supplier from {json_file.name}: {str(e)}")
                                continue
                        
                        # If we found suppliers in this file, we can stop (unless we need more)
                        if len(suppliers) >= limit:
                            break
                            
                except Exception as e:
                    logger.warning(f"Error reading {json_file.name}: {str(e)}")
                    continue
            
            logger.info(f"✅ Loaded {len(suppliers)} suppliers from fallback data")
            return suppliers[:limit * 2]  # Return extra for ranking
            
        except Exception as e:
            logger.error(f"Error loading fallback supplier data: {str(e)}")
            return []
    
    def _rank_and_filter(self, suppliers: List[Supplier], limit: int) -> List[Supplier]:
        """Rank suppliers by bestseller status, sales, rating, and response rate"""
        
        for supplier in suppliers:
            # Calculate comprehensive score
            # Prioritize: bestsellers > sales volume > rating > response rate
            bestseller_score = 100 if supplier.is_bestseller else 0
            sales_score = min((supplier.total_sold or 0) / 10, 100)  # Normalize to 100 max
            rating_score = supplier.rating * 20  # Scale to 100
            response_score = (supplier.response_rate or 0)
            verified_score = 50 if supplier.verified else 0
            
            supplier_score = (
                bestseller_score * 0.3 +      # 30% weight on bestseller status
                sales_score * 0.25 +          # 25% weight on sales volume
                rating_score * 0.25 +         # 25% weight on rating
                response_score * 0.15 +       # 15% weight on response rate
                verified_score * 0.05         # 5% weight on verification
            )
            
        # Sort by multiple criteria: bestseller > total_sold > rating
        sorted_suppliers = sorted(
            suppliers,
            key=lambda x: (
                x.is_bestseller,
                x.total_sold or 0,
                x.rating,
                x.response_rate or 0,
                x.verified
            ),
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
        """Generate a summary of supplier search with contact info and bestseller status"""
        if not suppliers:
            return "No suppliers found for your query."
            
        summary = f"Found {len(suppliers)} verified suppliers (sorted by bestsellers):\n\n"
        
        for i, supplier in enumerate(suppliers, 1):
            # Add bestseller badge
            badge = "🔥 BESTSELLER" if supplier.is_bestseller else ""
            summary += f"{i}. **{supplier.store_name}** ({supplier.marketplace}) {badge}\n"
            summary += f"   - Product: {supplier.product_name}\n"
            summary += f"   - Location: {supplier.city}\n"
            
            # Show rating and sales metrics
            if supplier.marketplace != "Indonetwork":
                summary += f"   - Rating: {supplier.rating}/5.0"
                if supplier.review_count:
                    summary += f" ({supplier.review_count} reviews)"
                summary += "\n"
                
                if supplier.total_sold:
                    summary += f"   - Total Sold: {supplier.total_sold:,} pcs\n"
                
                summary += f"   - Price: Rp {supplier.price:,.0f}\n"
            
            # Contact information (PRIORITY)
            contact_added = False
            if supplier.phone:
                summary += f"   - 📞 Phone: {supplier.phone}\n"
                contact_added = True
            if supplier.whatsapp and supplier.whatsapp != supplier.phone:
                summary += f"   - 💬 WhatsApp: {supplier.whatsapp}\n"
                contact_added = True
            if supplier.email:
                summary += f"   - 📧 Email: {supplier.email}\n"
                contact_added = True
            
            if not contact_added:
                summary += f"   - ℹ️ Contact: Available on marketplace page\n"
            
            # Additional info
            summary += f"   - Min Order: {supplier.minimum_order} pcs\n"
            summary += f"   - Stock: {'✅ Available' if supplier.stock_available else '❌ Out of Stock'}\n"
            
            if supplier.verified:
                summary += f"   - ✅ Verified Seller\n"
            
            if supplier.url:
                summary += f"   - 🔗 Link: {supplier.url}\n"
            
            summary += "\n"
        
        # Add summary stats
        bestseller_count = sum(1 for s in suppliers if s.is_bestseller)
        with_contact = sum(1 for s in suppliers if s.phone or s.email)
        
        summary += f"\n📊 Summary:\n"
        summary += f"- {bestseller_count}/{len(suppliers)} are bestsellers\n"
        summary += f"- {with_contact}/{len(suppliers)} have contact information\n"
        summary += f"- Average rating: {sum(s.rating for s in suppliers) / len(suppliers):.1f}/5.0\n"
            
        return summary
