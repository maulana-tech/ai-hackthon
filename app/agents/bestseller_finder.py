"""
BestsellerFinder Agent - Advanced product discovery based on marketplace sales data

This agent finds the most popular/bestselling products from Indonesian marketplaces
by analyzing:
- Sales volume (total sold)
- Rating and review count
- Seller badge (official store, mall)
- Price trends
- Search ranking
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from app.models.schemas import TrendingProduct, Supplier
from app.integrations.apify_client import ApifyIntegration
from app.integrations.firecrawl_client import FirecrawlClient
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BestsellerFinder:
    """
    Agent to discover bestselling products from Indonesian marketplaces
    Uses real-time marketplace data to identify trending/popular items
    """
    
    def __init__(self):
        self.apify = ApifyIntegration()
        self.firecrawl = FirecrawlClient()
        self.name = "Bestseller Finder Agent"
        
    async def find_bestsellers(
        self,
        category: Optional[str] = None,
        marketplace: Optional[str] = None,
        limit: int = 10,
        min_sold: int = 100,
        min_rating: float = 4.0
    ) -> List[TrendingProduct]:
        """
        Find bestselling products across marketplaces
        
        Args:
            category: Product category (e.g., "fashion", "electronics", "beauty")
            marketplace: Specific marketplace ("tokopedia", "shopee", "lazada") or None for all
            limit: Max products to return
            min_sold: Minimum units sold
            min_rating: Minimum product rating
            
        Returns:
            List of TrendingProduct sorted by sales volume
        """
        logger.info(f"Finding bestsellers - category: {category}, marketplace: {marketplace}")
        
        # Determine which marketplaces to scrape
        marketplaces = []
        if marketplace:
            marketplaces = [marketplace.lower()]
        else:
            marketplaces = ["tokopedia", "shopee", "indonetwork"]
        
        # Scrape all marketplaces in parallel
        tasks = []
        for mp in marketplaces:
            if mp == "tokopedia":
                tasks.append(self._scrape_tokopedia_bestsellers(category, limit * 2))
            elif mp == "shopee":
                tasks.append(self._scrape_shopee_bestsellers(category, limit * 2))
            elif mp == "indonetwork":
                tasks.append(self._scrape_indonetwork_bestsellers(category, limit * 2))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine and filter results
        all_products = []
        for result in results:
            if isinstance(result, list):
                all_products.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Marketplace scrape failed: {str(result)}")
        
        # Filter by criteria
        filtered = [
            p for p in all_products
            if (p.total_sold or 0) >= min_sold and p.rating >= min_rating
        ]
        
        # Rank by sales volume, rating, and trend score
        ranked = self._rank_products(filtered, limit)
        
        logger.info(f"Found {len(ranked)} bestselling products")
        return ranked
    
    async def _scrape_tokopedia_bestsellers(
        self,
        category: Optional[str],
        limit: int
    ) -> List[TrendingProduct]:
        """Scrape Tokopedia bestsellers"""
        try:
            logger.info(f"Scraping Tokopedia bestsellers - category: {category}")
            
            # Build search query based on category
            if category:
                search_query = self._category_to_query(category)
            else:
                # Use general bestseller page
                search_query = "terlaris"
            
            # Scrape with Firecrawl (faster than Apify for bestseller pages)
            url = f"https://www.tokopedia.com/search?q={search_query}&ob=5"  # ob=5 = sort by sales
            
            result = await self.firecrawl.scrape(
                url,
                formats=[{
                    "type": "json",
                    "prompt": """Extract bestselling products with these fields:
                    - product_name
                    - price
                    - rating (out of 5)
                    - total_sold (terjual)
                    - review_count
                    - shop_name
                    - shop_location
                    - product_url
                    - is_official_store (boolean)
                    - image_url
                    
                    Focus on products with highest 'terjual' (sold) count.
                    """
                }]
            )
            
            products = []
            
            if result and 'data' in result and 'json' in result['data']:
                json_data = result['data']['json']
                
                items = []
                if isinstance(json_data, dict):
                    items = json_data.get('products', json_data.get('items', []))
                elif isinstance(json_data, list):
                    items = json_data
                
                for item in items[:limit]:
                    try:
                        # Extract total sold
                        total_sold = self._extract_number(item.get('total_sold', '0'))
                        
                        # Extract price
                        price_str = str(item.get('price', '0'))
                        price = self._extract_number(price_str)
                        
                        product = TrendingProduct(
                            name=item.get('product_name', item.get('name', 'Unknown Product')),
                            category=category or self._infer_category(item.get('product_name', '')),
                            trend_score=self._calculate_trend_score(
                                total_sold=total_sold,
                                rating=float(item.get('rating', 4.0)),
                                review_count=int(item.get('review_count', 0)),
                                is_official=item.get('is_official_store', False)
                            ),
                            growth_percentage=50.0,  # Estimate based on bestseller status
                            search_volume=total_sold,
                            region="Indonesia",
                            platform="Tokopedia",
                            description=item.get('description', ''),
                            image_url=item.get('image_url', ''),
                            price_range=f"Rp {price:,.0f}" if price > 0 else "Varies",
                            keywords=[search_query],
                            # Extended attributes
                            rating=float(item.get('rating', 4.0)),
                            total_sold=total_sold,
                            review_count=int(item.get('review_count', 0)),
                            shop_name=item.get('shop_name', ''),
                            shop_location=item.get('shop_location', ''),
                            product_url=item.get('product_url', ''),
                            is_official=item.get('is_official_store', False)
                        )
                        
                        products.append(product)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing Tokopedia item: {str(e)}")
                        continue
            
            logger.info(f"Found {len(products)} products from Tokopedia")
            return products
            
        except Exception as e:
            logger.error(f"Tokopedia bestseller scrape error: {str(e)}")
            return []
    
    async def _scrape_shopee_bestsellers(
        self,
        category: Optional[str],
        limit: int
    ) -> List[TrendingProduct]:
        """Scrape Shopee bestsellers"""
        try:
            logger.info(f"Scraping Shopee bestsellers - category: {category}")
            
            if category:
                search_query = self._category_to_query(category)
            else:
                search_query = "terlaris"
            
            # Shopee URL with sort by sales
            url = f"https://shopee.co.id/search?keyword={search_query}&sortBy=sales"
            
            result = await self.firecrawl.scrape(
                url,
                formats=[{
                    "type": "json",
                    "prompt": """Extract bestselling products with:
                    - name
                    - price
                    - rating
                    - sold (historical_sold)
                    - review_count
                    - shop_name
                    - shop_location
                    - url
                    - is_official_shop or is_mall
                    - image_url
                    
                    Prioritize products with highest sold count.
                    """
                }]
            )
            
            products = []
            
            if result and 'data' in result and 'json' in result['data']:
                json_data = result['data']['json']
                
                items = []
                if isinstance(json_data, dict):
                    items = json_data.get('products', json_data.get('items', []))
                elif isinstance(json_data, list):
                    items = json_data
                
                for item in items[:limit]:
                    try:
                        total_sold = self._extract_number(item.get('sold', item.get('historical_sold', '0')))
                        price = self._extract_number(str(item.get('price', '0')))
                        
                        product = TrendingProduct(
                            name=item.get('name', 'Unknown Product'),
                            category=category or self._infer_category(item.get('name', '')),
                            trend_score=self._calculate_trend_score(
                                total_sold=total_sold,
                                rating=float(item.get('rating', 4.0)),
                                review_count=int(item.get('review_count', 0)),
                                is_official=item.get('is_official_shop', item.get('is_mall', False))
                            ),
                            growth_percentage=50.0,
                            search_volume=total_sold,
                            region="Indonesia",
                            platform="Shopee",
                            description=item.get('description', ''),
                            image_url=item.get('image_url', ''),
                            price_range=f"Rp {price:,.0f}" if price > 0 else "Varies",
                            keywords=[search_query],
                            rating=float(item.get('rating', 4.0)),
                            total_sold=total_sold,
                            review_count=int(item.get('review_count', 0)),
                            shop_name=item.get('shop_name', ''),
                            shop_location=item.get('shop_location', ''),
                            product_url=item.get('url', ''),
                            is_official=item.get('is_official_shop', item.get('is_mall', False))
                        )
                        
                        products.append(product)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing Shopee item: {str(e)}")
                        continue
            
            logger.info(f"Found {len(products)} products from Shopee")
            return products
            
        except Exception as e:
            logger.error(f"Shopee bestseller scrape error: {str(e)}")
            return []
    
    async def _scrape_indonetwork_bestsellers(
        self,
        category: Optional[str],
        limit: int
    ) -> List[TrendingProduct]:
        """Scrape Indonetwork popular B2B products"""
        try:
            logger.info(f"Scraping Indonetwork bestsellers - category: {category}")
            
            if category:
                search_query = self._category_to_query(category)
            else:
                search_query = "produk populer"
            
            url = f"https://www.indonetwork.co.id/search?q={search_query.replace(' ', '+')}"
            
            result = await self.firecrawl.scrape(
                url,
                formats=[{
                    "type": "json",
                    "prompt": """Extract popular B2B products with:
                    - product_name
                    - supplier_name
                    - location
                    - minimum_order
                    - price (if available)
                    - product_url
                    - category
                    
                    Focus on verified suppliers and popular products.
                    """
                }]
            )
            
            products = []
            
            if result and 'data' in result and 'json' in result['data']:
                json_data = result['data']['json']
                
                items = []
                if isinstance(json_data, dict):
                    items = json_data.get('products', json_data.get('items', []))
                elif isinstance(json_data, list):
                    items = json_data
                
                for item in items[:limit]:
                    try:
                        product = TrendingProduct(
                            name=item.get('product_name', 'Unknown Product'),
                            category=category or item.get('category', 'B2B'),
                            trend_score=75.0,  # B2B products are generally popular if listed
                            growth_percentage=40.0,
                            search_volume=5000,  # Estimate for B2B
                            region="Indonesia",
                            platform="Indonetwork",
                            description=item.get('description', ''),
                            price_range=item.get('price', 'Contact Supplier'),
                            keywords=[search_query],
                            rating=4.5,  # Default for B2B verified
                            shop_name=item.get('supplier_name', ''),
                            shop_location=item.get('location', ''),
                            product_url=item.get('product_url', ''),
                            is_official=True  # Indonetwork suppliers are verified
                        )
                        
                        products.append(product)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing Indonetwork item: {str(e)}")
                        continue
            
            logger.info(f"Found {len(products)} products from Indonetwork")
            return products
            
        except Exception as e:
            logger.error(f"Indonetwork bestseller scrape error: {str(e)}")
            return []
    
    def _calculate_trend_score(
        self,
        total_sold: int,
        rating: float,
        review_count: int,
        is_official: bool
    ) -> float:
        """
        Calculate trend score based on multiple factors
        
        Score = (sales_score * 0.4) + (rating_score * 0.3) + (review_score * 0.2) + (official_bonus * 0.1)
        """
        # Normalize sales (log scale to prevent extreme values)
        import math
        sales_score = min(math.log10(total_sold + 1) * 10, 100) if total_sold > 0 else 0
        
        # Rating score (out of 5 -> out of 100)
        rating_score = rating * 20
        
        # Review score (log scale)
        review_score = min(math.log10(review_count + 1) * 15, 100) if review_count > 0 else 0
        
        # Official store bonus
        official_bonus = 100 if is_official else 50
        
        # Weighted average
        trend_score = (
            sales_score * 0.4 +
            rating_score * 0.3 +
            review_score * 0.2 +
            official_bonus * 0.1
        )
        
        return round(trend_score, 2)
    
    def _rank_products(self, products: List[TrendingProduct], limit: int) -> List[TrendingProduct]:
        """Rank products by multiple factors"""
        
        # Sort by: trend_score (primary), total_sold (secondary), rating (tertiary)
        sorted_products = sorted(
            products,
            key=lambda p: (
                p.trend_score,
                p.total_sold or 0,
                p.rating or 0,
                p.is_official
            ),
            reverse=True
        )
        
        return sorted_products[:limit]
    
    def _category_to_query(self, category: str) -> str:
        """Convert category to Indonesian search query"""
        category_mapping = {
            "fashion": "fashion terlaris",
            "pakaian": "pakaian terlaris",
            "electronics": "elektronik terlaris",
            "elektronik": "elektronik terlaris",
            "beauty": "kecantikan terlaris",
            "kecantikan": "kecantikan terlaris",
            "skincare": "skincare terlaris",
            "health": "kesehatan terlaris",
            "kesehatan": "kesehatan terlaris",
            "home": "rumah tangga terlaris",
            "food": "makanan terlaris",
            "makanan": "makanan terlaris",
            "toys": "mainan terlaris",
            "mainan": "mainan terlaris",
            "accessories": "aksesoris terlaris",
            "aksesoris": "aksesoris terlaris"
        }
        
        return category_mapping.get(category.lower(), f"{category} terlaris")
    
    def _infer_category(self, product_name: str) -> str:
        """Infer category from product name"""
        name_lower = product_name.lower()
        
        if any(word in name_lower for word in ['baju', 'celana', 'dress', 'kemeja', 'fashion', 'pakaian']):
            return "Fashion"
        elif any(word in name_lower for word in ['skincare', 'serum', 'cream', 'makeup', 'beauty']):
            return "Beauty"
        elif any(word in name_lower for word in ['laptop', 'hp', 'phone', 'elektronik', 'gadget']):
            return "Electronics"
        elif any(word in name_lower for word in ['tas', 'sepatu', 'jam', 'aksesoris']):
            return "Accessories"
        elif any(word in name_lower for word in ['makanan', 'snack', 'minuman', 'food']):
            return "Food"
        else:
            return "General"
    
    def _extract_number(self, text: str) -> int:
        """Extract number from text (e.g., '1.5rb' -> 1500, '10k' -> 10000)"""
        if not text:
            return 0
        
        text = str(text).lower().strip()
        
        # Handle Indonesian/international abbreviations
        multipliers = {
            'rb': 1000,      # ribu (thousand)
            'k': 1000,       # thousand
            'jt': 1000000,   # juta (million)
            'm': 1000000,    # million
        }
        
        # Extract number and suffix
        match = re.search(r'([\d.,]+)\s*([a-z]+)?', text)
        if match:
            number_str = match.group(1).replace('.', '').replace(',', '.')
            suffix = match.group(2) or ''
            
            try:
                number = float(number_str)
                multiplier = multipliers.get(suffix, 1)
                return int(number * multiplier)
            except ValueError:
                return 0
        
        return 0
    
    async def generate_bestseller_report(
        self,
        products: List[TrendingProduct],
        include_suppliers: bool = False
    ) -> str:
        """Generate detailed report of bestselling products"""
        
        if not products:
            return "❌ No bestselling products found."
        
        report = f"""
🔥 **BESTSELLER PRODUCTS REPORT**
{'='*70}

Found {len(products)} trending products across Indonesian marketplaces

"""
        
        for i, product in enumerate(products, 1):
            report += f"""
{i}. **{product.name}** 
   📊 Trend Score: {product.trend_score:.1f}/100
   ⭐ Rating: {product.rating:.1f}/5.0 ({product.review_count:,} reviews)
   🛒 Total Sold: {product.total_sold:,} units
   💰 Price: {product.price_range}
   🏪 Platform: {product.platform}
   📍 Location: {product.shop_location or 'Indonesia'}
   {'✅ Official Store' if product.is_official else ''}
   
"""
        
        # Summary statistics
        total_sold_sum = sum(p.total_sold or 0 for p in products)
        avg_rating = sum(p.rating or 0 for p in products) / len(products)
        official_count = sum(1 for p in products if p.is_official)
        
        report += f"""
{'='*70}
📈 **SUMMARY STATISTICS**

- Total Combined Sales: {total_sold_sum:,} units
- Average Rating: {avg_rating:.2f}/5.0
- Official Stores: {official_count}/{len(products)}
- Top Platform: {max(set(p.platform for p in products), key=lambda x: sum(1 for p in products if p.platform == x))}

"""
        
        return report
