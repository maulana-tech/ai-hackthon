import asyncio
import logging
from typing import List, Dict, Any, Optional
from apify_client import ApifyClient

from app.config import get_settings
from app.models.schemas import Supplier

logger = logging.getLogger(__name__)
settings = get_settings()


class ApifyIntegration:
    """
    Apify API client for web scraping Indonesian marketplaces
    
    Supports:
    - Tokopedia scraping (jupri/tokopedia-scraper)
    - Lazada scraping (getdataforme/lazada-product-scraper)
    - Instagram trend analysis
    - TikTok viral products
    
    Actor Configuration:
    - Tokopedia: jupri/tokopedia-scraper
    - Lazada: getdataforme/lazada-product-scraper (Malaysia/Indonesia)
    
    Notes:
    - Shopee removed (socket hang up errors, unstable)
    - Lazada re-added with proper actor (getdataforme)
    """
    
    # Actor names (verified and working)
    TOKOPEDIA_ACTOR = "jupri/tokopedia-scraper"
    LAZADA_ACTOR = "getdataforme/lazada-product-scraper"
    
    def __init__(self):
        self.client = ApifyClient(settings.apify_api_key)
        self.name = "Apify Integration"
        
    async def scrape_tokopedia(
        self,
        product_name: str,
        max_items: int = 50,
        min_rating: float = 4.0
    ) -> List[Dict[str, Any]]:
        """
        Scrape Tokopedia for products and suppliers
        
        Args:
            product_name: Search query
            max_items: Maximum products to scrape
            min_rating: Minimum seller rating
            
        Returns:
            List of product/supplier data
        """
        try:
            logger.info(f"Scraping Tokopedia: {product_name}")
            
            # Correct input format based on jupri/tokopedia-scraper docs
            # Uses Tokopedia Query Language (TPQL)
            run_input = {
                "query": [product_name],  # Array of search queries
                "limit": max_items,       # Number of results per query
                "filters": {}             # Optional filters
            }
            
            # Run actor (using verified actor name)
            run = await asyncio.to_thread(
                lambda: self.client.actor(self.TOKOPEDIA_ACTOR).call(run_input=run_input)
            )
            
            # Get results
            items = []
            dataset = self.client.dataset(run["defaultDatasetId"])
            
            for item in dataset.iterate_items():
                # Filter by rating
                seller_rating = item.get("sellerRating", 0)
                if seller_rating >= min_rating:
                    items.append(item)
                    
            logger.info(f"Scraped {len(items)} products from Tokopedia")
            return items
            
        except Exception as e:
            logger.error(f"Tokopedia scrape error: {str(e)}")
            return []
    
    # Shopee scraper removed due to unstable actor (socket hang up errors)
    # Error: "socket hang up" when making API requests
    # If you want to re-enable, fix actor or use different Shopee actor
    
    # async def scrape_shopee(
    #     self,
    #     product_name: str,
    #     max_items: int = 50,
    #     min_rating: float = 4.0
    # ) -> List[Dict[str, Any]]:
    #     """
    #     Scrape Shopee Indonesia for products
    #     
    #     Args:
    #         product_name: Search query
    #         max_items: Maximum products to scrape
    #         min_rating: Minimum shop rating
    #         
    #     Returns:
    #         List of product/shop data
    #     """
    #     try:
    #         logger.info(f"Scraping Shopee: {product_name}")
    #         
    #         # Correct input format based on best_scraper/shopee-scraper docs
    #         # Uses Shopee API with direct requests
    #         import urllib.parse
    #         encoded_keyword = urllib.parse.quote(product_name)
    #         
    #         run_input = {
    #             "requests": [
    #                 {
    #                     "url": f"https://shopee.co.id/api/v4/search/search_items?keyword={encoded_keyword}&limit={max_items}&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2",
    #                     "method": "GET"
    #                 }
    #             ],
    #             "cookie": ""  # Optional: Add Shopee cookies for better access
    #         }
    #         
    #         run = await asyncio.to_thread(
    #             lambda: self.client.actor("best_scraper/shopee-scraper").call(run_input=run_input)
    #         )
    #         
    #         items = []
    #         dataset = self.client.dataset(run["defaultDatasetId"])
    #         
    #         # Parse Shopee API response
    #         # Format: [{"data": {"items": [...]}}]
    #         for response in dataset.iterate_items():
    #             if isinstance(response, dict):
    #                 # Get items from API response
    #                 data = response.get("data", {})
    #                 search_items = data.get("items", [])
    #                 
    #                 for item in search_items:
    #                     # Shopee API returns item data differently
    #                     item_basic = item.get("item_basic", item)
    #                     shop_rating = item_basic.get("shop_rating", 0)
    #                     
    #                     if shop_rating >= min_rating:
    #                         items.append(item_basic)
    #             else:
    #                 # Fallback for old format
    #                 shop_rating = response.get("shopRating", 0)
    #                 if shop_rating >= min_rating:
    #                     items.append(response)
    #                     
    #         logger.info(f"Scraped {len(items)} products from Shopee")
    #         return items
    #         
    #     except Exception as e:
    #         logger.error(f"Shopee scrape error: {str(e)}")
    #         return []
    
    async def scrape_lazada(
        self,
        product_name: str,
        max_items: int = 50,
        min_rating: float = 4.0
    ) -> List[Dict[str, Any]]:
        """
        Scrape Lazada for products using getdataforme/lazada-product-scraper
        
        Args:
            product_name: Search query
            max_items: Maximum products to scrape
            min_rating: Minimum product rating (0-5)
            
        Returns:
            List of product data with URLs, prices, ratings, etc.
        """
        try:
            logger.info(f"Scraping Lazada: {product_name}")
            
            # Correct input format for getdataforme/lazada-product-scraper
            run_input = {
                "query": product_name,
                "item_limit": max_items,
                "proxyConfiguration": {
                    "useApifyProxy": True,
                    "apifyProxyGroups": ["RESIDENTIAL"],
                    "apifyProxyCountry": "MY"  # Malaysia (also works for Indonesia)
                }
            }
            
            run = await asyncio.to_thread(
                lambda: self.client.actor(self.LAZADA_ACTOR).call(run_input=run_input)
            )
            
            items = []
            dataset = self.client.dataset(run["defaultDatasetId"])
            
            for item in dataset.iterate_items():
                # Filter by rating (Lazada uses rating_score out of 5)
                rating = float(item.get("rating_score", 0))
                if rating >= min_rating:
                    # Normalize data structure
                    product = {
                        "product_id": item.get("product_id"),
                        "name": item.get("product_name"),
                        "url": item.get("product_url"),
                        "price": item.get("price"),
                        "original_price": item.get("original_price"),
                        "rating": rating,
                        "review_count": int(item.get("review_count", 0)),
                        "location": item.get("location"),
                        "seller_name": item.get("seller_name"),
                        "seller_id": item.get("seller_id"),
                        "brand": item.get("brand"),
                        "image_url": item.get("image_url"),
                        "in_stock": item.get("in_stock", True),
                        "platform": "Lazada"
                    }
                    items.append(product)
                    
            logger.info(f"Scraped {len(items)} products from Lazada")
            return items
            
        except Exception as e:
            logger.error(f"Lazada scrape error: {str(e)}")
            return []
    
    async def scrape_instagram_hashtag(
        self,
        hashtag: str,
        max_posts: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Scrape Instagram hashtag for trend analysis
        
        Args:
            hashtag: Hashtag to search (without #)
            max_posts: Maximum posts to scrape
            
        Returns:
            List of Instagram posts
        """
        try:
            logger.info(f"Scraping Instagram: #{hashtag}")
            
            run_input = {
                "hashtags": [hashtag],
                "resultsLimit": max_posts
            }
            
            run = await asyncio.to_thread(
                lambda: self.client.actor("apify/instagram-scraper").call(run_input=run_input)
            )
            
            posts = []
            dataset = self.client.dataset(run["defaultDatasetId"])
            
            for item in dataset.iterate_items():
                posts.append(item)
                
            logger.info(f"Scraped {len(posts)} Instagram posts")
            return posts
            
        except Exception as e:
            logger.error(f"Instagram scrape error: {str(e)}")
            return []
    
    async def scrape_tiktok_hashtag(
        self,
        hashtag: str,
        max_videos: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Scrape TikTok hashtag for viral products
        
        Args:
            hashtag: Hashtag to search (without #)
            max_videos: Maximum videos to scrape
            
        Returns:
            List of TikTok videos
        """
        try:
            logger.info(f"Scraping TikTok: #{hashtag}")
            
            run_input = {
                "hashtags": [hashtag],
                "resultsPerPage": max_videos
            }
            
            run = await asyncio.to_thread(
                lambda: self.client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
            )
            
            videos = []
            dataset = self.client.dataset(run["defaultDatasetId"])
            
            for item in dataset.iterate_items():
                videos.append(item)
                
            logger.info(f"Scraped {len(videos)} TikTok videos")
            return videos
            
        except Exception as e:
            logger.error(f"TikTok scrape error: {str(e)}")
            return []
    
    async def scrape_all_marketplaces(
        self,
        product_name: str,
        max_items_per_marketplace: int = 20,
        min_rating: float = 4.0
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrape all Indonesian marketplaces in parallel
        
        Args:
            product_name: Product to search
            max_items_per_marketplace: Max items per marketplace
            min_rating: Minimum seller rating
            
        Returns:
            Dict with results from each marketplace
        """
        try:
            logger.info(f"Scraping all marketplaces: {product_name}")
            
            # Run all scrapers in parallel (Shopee removed - unstable)
            results = await asyncio.gather(
                self.scrape_tokopedia(product_name, max_items_per_marketplace, min_rating),
                self.scrape_lazada(product_name, max_items_per_marketplace, min_rating),
                return_exceptions=True
            )
            
            tokopedia, lazada = results
            shopee = []  # Shopee disabled
            
            return {
                "tokopedia": tokopedia if isinstance(tokopedia, list) else [],
                "shopee": shopee if isinstance(shopee, list) else [],
                "lazada": lazada if isinstance(lazada, list) else []
            }
            
        except Exception as e:
            logger.error(f"Multi-marketplace scrape error: {str(e)}")
            return {"tokopedia": [], "shopee": [], "lazada": []}
    
    def parse_to_supplier(
        self,
        item: Dict[str, Any],
        marketplace: str
    ) -> Supplier:
        """
        Parse marketplace data to Supplier model
        
        Args:
            item: Raw data from marketplace
            marketplace: Source marketplace name
            
        Returns:
            Supplier object
        """
        try:
            if marketplace == "tokopedia":
                return Supplier(
                    name=item.get("sellerName", "Unknown"),
                    store_name=item.get("shopName", "Unknown"),
                    marketplace="Tokopedia",
                    location=item.get("shopLocation", "Indonesia"),
                    rating=item.get("sellerRating", 0.0),
                    product_name=item.get("name", ""),
                    price=item.get("price", 0),
                    currency="IDR",
                    moq=item.get("minOrder", 1),
                    stock_available=item.get("stock", 0) > 0,
                    phone=item.get("phone", ""),
                    email=item.get("email", ""),
                    product_url=item.get("url", ""),
                    image_url=item.get("image", "")
                )
            
            elif marketplace == "shopee":
                return Supplier(
                    name=item.get("shopName", "Unknown"),
                    store_name=item.get("shopName", "Unknown"),
                    marketplace="Shopee",
                    location=item.get("shopLocation", "Indonesia"),
                    rating=item.get("shopRating", 0.0),
                    product_name=item.get("name", ""),
                    price=item.get("price", 0),
                    currency="IDR",
                    moq=item.get("minPurchase", 1),
                    stock_available=item.get("stock", 0) > 0,
                    phone=item.get("phone", ""),
                    email=item.get("email", ""),
                    product_url=item.get("url", ""),
                    image_url=item.get("image", "")
                )
            
            elif marketplace == "lazada":
                return Supplier(
                    name=item.get("sellerName", "Unknown"),
                    store_name=item.get("sellerName", "Unknown"),
                    marketplace="Lazada",
                    location=item.get("sellerLocation", "Indonesia"),
                    rating=item.get("sellerRating", 0.0),
                    product_name=item.get("name", ""),
                    price=item.get("price", 0),
                    currency="IDR",
                    moq=1,
                    stock_available=True,
                    phone=item.get("phone", ""),
                    email=item.get("email", ""),
                    product_url=item.get("url", ""),
                    image_url=item.get("image", "")
                )
            
            else:
                raise ValueError(f"Unknown marketplace: {marketplace}")
                
        except Exception as e:
            logger.error(f"Error parsing supplier: {str(e)}")
            return None
    
    async def get_suppliers_from_all_marketplaces(
        self,
        product_name: str,
        max_suppliers: int = 20,
        min_rating: float = 4.0
    ) -> List[Supplier]:
        """
        Get suppliers from all marketplaces as Supplier objects
        
        Args:
            product_name: Product to search
            max_suppliers: Maximum suppliers to return
            min_rating: Minimum rating filter
            
        Returns:
            List of Supplier objects
        """
        try:
            # Scrape all marketplaces
            raw_results = await self.scrape_all_marketplaces(
                product_name,
                max_items_per_marketplace=max_suppliers // 3,
                min_rating=min_rating
            )
            
            suppliers = []
            
            # Parse Tokopedia results
            for item in raw_results["tokopedia"]:
                supplier = self.parse_to_supplier(item, "tokopedia")
                if supplier:
                    suppliers.append(supplier)
            
            # Parse Shopee results
            for item in raw_results["shopee"]:
                supplier = self.parse_to_supplier(item, "shopee")
                if supplier:
                    suppliers.append(supplier)
            
            # Parse Lazada results
            for item in raw_results["lazada"]:
                supplier = self.parse_to_supplier(item, "lazada")
                if supplier:
                    suppliers.append(supplier)
            
            # Sort by rating
            suppliers.sort(key=lambda s: s.rating, reverse=True)
            
            # Return top N
            return suppliers[:max_suppliers]
            
        except Exception as e:
            logger.error(f"Error getting suppliers: {str(e)}")
            return []
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get Apify account usage statistics"""
        try:
            user_info = await asyncio.to_thread(lambda: self.client.user().get())
            
            return {
                "success": True,
                "usage": {
                    "credits_used": user_info.get("usage", {}).get("monthUsage", 0),
                    "credits_limit": user_info.get("usage", {}).get("monthLimit", 0),
                }
            }
        except Exception as e:
            logger.error(f"Error getting usage stats: {str(e)}")
            return {"success": False, "error": str(e)}
