"""
Local Scrape Data Loader

Loads pre-scraped marketplace data as an alternative to Firecrawl API
when API credits are depleted or for faster response times.
"""
import json
import os
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class LocalScrapeData:
    """Load and search local scraped marketplace data"""
    
    def __init__(self):
        self.data_path = Path(__file__).parent.parent.parent / "data" / "scraping_results" / "scrape.json"
        self._data: List[Dict[str, Any]] = []
        self._loaded = False
        
    def _load_data(self):
        """Load data from JSON file"""
        if self._loaded:
            return
            
        try:
            if self.data_path.exists():
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                logger.info(f"Loaded {len(self._data)} shops from local scrape data")
                self._loaded = True
            else:
                logger.warning(f"Local scrape data not found: {self.data_path}")
                self._data = []
        except Exception as e:
            logger.error(f"Error loading local scrape data: {str(e)}")
            self._data = []
    
    def search_products(
        self,
        query: str,
        limit: int = 10,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search products from local scraped data
        
        Args:
            query: Search query (product name/category)
            limit: Maximum products to return
            min_price: Minimum price filter
            max_price: Maximum price filter
            
        Returns:
            List of products matching criteria
        """
        self._load_data()
        
        if not self._data:
            return []
        
        query_lower = query.lower()
        matching_products = []
        
        # Search through all shops and their products
        for shop in self._data:
            shop_info = {
                'shop_name': shop.get('name', ''),
                'shop_location': shop.get('location', ''),
                'shop_url': shop.get('url', ''),
                'is_official': shop.get('is_official', False),
                'description': shop.get('description', '')
            }
            
            products = shop.get('products', [])
            
            for product in products:
                product_name = product.get('name', '').lower()
                
                # Check if query matches product name
                if query_lower in product_name or any(word in product_name for word in query_lower.split()):
                    price = product.get('price', 0)
                    
                    # Apply price filters
                    if min_price and price < min_price:
                        continue
                    if max_price and price > max_price:
                        continue
                    
                    # Combine product with shop info
                    product_data = {
                        **product,
                        **shop_info,
                        'platform': 'Tokopedia'
                    }
                    
                    matching_products.append(product_data)
                    
                    if len(matching_products) >= limit * 3:  # Get more for sorting
                        break
            
            if len(matching_products) >= limit * 3:
                break
        
        # Sort by relevance (name match) and price
        def relevance_score(p):
            name = p.get('name', '').lower()
            # Exact match = higher score
            if query_lower == name:
                return 1000
            # Starts with query = high score
            if name.startswith(query_lower):
                return 500
            # Contains query = medium score
            if query_lower in name:
                return 100
            # Individual words match = low score
            return sum(10 for word in query_lower.split() if word in name)
        
        matching_products.sort(key=relevance_score, reverse=True)
        
        logger.info(f"Found {len(matching_products)} products for query: {query}")
        
        return matching_products[:limit]
    
    def get_shop_products(self, shop_domain: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get products from a specific shop"""
        self._load_data()
        
        for shop in self._data:
            if shop.get('domain') == shop_domain:
                products = shop.get('products', [])[:limit]
                
                # Add shop info to each product
                for product in products:
                    product['shop_name'] = shop.get('name', '')
                    product['shop_location'] = shop.get('location', '')
                    product['shop_url'] = shop.get('url', '')
                    product['platform'] = 'Tokopedia'
                
                return products
        
        return []
    
    def get_all_shops(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all shops from data"""
        self._load_data()
        
        shops = []
        for shop in self._data:
            shops.append({
                'name': shop.get('name', ''),
                'domain': shop.get('domain', ''),
                'location': shop.get('location', ''),
                'description': shop.get('description', ''),
                'url': shop.get('url', ''),
                'is_official': shop.get('is_official', False),
                'total_products': len(shop.get('products', [])),
                'platform': 'Tokopedia'
            })
        
        if limit:
            shops = shops[:limit]
        
        return shops
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded data"""
        self._load_data()
        
        total_products = sum(len(shop.get('products', [])) for shop in self._data)
        
        return {
            'total_shops': len(self._data),
            'total_products': total_products,
            'avg_products_per_shop': total_products / len(self._data) if self._data else 0,
            'data_source': 'local_scrape_json',
            'status': 'loaded' if self._loaded else 'not_loaded'
        }


# Global instance
local_scrape_data = LocalScrapeData()
