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
    SHOPEE_ACTOR = "best_scraper/shopee-scraper"  # User specified
    
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
            logger.info(f"🔍 Scraping Tokopedia: {product_name}")
            
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
                # Filter by rating (use multiple possible fields)
                # Convert to float to handle string ratings
                try:
                    seller_rating = float(item.get("sellerRating", 0) or 0)
                    shop_rating = float(item.get("shopRating", 0) or 0)
                    product_rating = float(item.get("rating", 0) or 0)
                except (ValueError, TypeError):
                    seller_rating = shop_rating = product_rating = 0
                
                # Use the highest rating available
                max_rating = max(seller_rating, shop_rating, product_rating)
                
                # More lenient filter - accept if any rating meets threshold or no rating info
                if max_rating >= min_rating or max_rating == 0:
                    items.append(item)
                    
            logger.info(f"✅ Scraped {len(items)} products from Tokopedia (filtered from dataset)")
            return items
            
        except Exception as e:
            error_msg = str(e)
            if "exceed your remaining usage" in error_msg:
                logger.warning(f"⚠️ Apify credits exhausted for Tokopedia")
            else:
                logger.error(f"❌ Tokopedia scrape error: {error_msg}")
            return []
    
    async def scrape_shopee(
        self,
        product_name: str,
        max_items: int = 50,
        min_rating: float = 4.0
    ) -> List[Dict[str, Any]]:
        """
        Scrape Shopee Indonesia for products using best_scraper/shopee-scraper
        
        This actor uses Shopee's unofficial API and requires proper URL format.
        Optional: Add Shopee cookies for better access (set in environment)
        
        Args:
            product_name: Search query
            max_items: Maximum products to scrape (limit per API call: 60)
            min_rating: Minimum shop rating
            
        Returns:
            List of product/shop data
        """
        try:
            logger.info(f"🔍 Scraping Shopee: {product_name}")
            
            # Format according to best_scraper/shopee-scraper documentation
            # Use proper Shopee API v4 endpoint with all required parameters
            import urllib.parse
            encoded_keyword = urllib.parse.quote(product_name)
            
            # Limit to 60 per Shopee API restrictions
            api_limit = min(max_items, 60)
            
            run_input = {
                "requests": [
                    {
                        # Shopee Indonesia API v4 search endpoint
                        "url": f"https://shopee.co.id/api/v4/search/search_items?by=relevancy&keyword={encoded_keyword}&limit={api_limit}&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2",
                        "method": "GET"
                    }
                ],
                # Optional: Add cookies from environment variable if available
                "cookie": settings.shopee_cookies if hasattr(settings, 'shopee_cookies') else ""
            }
            
            run = await asyncio.to_thread(
                lambda: self.client.actor(self.SHOPEE_ACTOR).call(run_input=run_input)
            )
            
            items = []
            dataset = self.client.dataset(run["defaultDatasetId"])
            
            # Parse Shopee API response
            # Expected format can be:
            # 1. Official API: [{"data": {"items": [...]}}]
            # 2. Scraped data: [{"network": "Shopee", "title": "...", "email": "...", ...}]
            for response in dataset.iterate_items():
                if not isinstance(response, dict):
                    continue
                
                # Check if this is scraped supplier data format (with email field)
                if "network" in response and response.get("network") == "Shopee":
                    # This is pre-scraped supplier data
                    # Convert to standard format
                    supplier_item = {
                        "name": response.get("title", "N/A"),
                        "title": response.get("title", "N/A"),
                        "description": response.get("description", ""),
                        "url": response.get("url", ""),
                        "email": response.get("email", ""),
                        "supplier_email": response.get("email", ""),
                        "keyword": response.get("keyword", ""),
                        "platform": "Shopee",
                        "rating": 4.5,  # Default good rating for suppliers with email
                        "shop_rating": 4.5
                    }
                    items.append(supplier_item)
                    continue
                
                # Standard Shopee API format
                data = response.get("data", {})
                search_items = data.get("items", [])
                
                if not search_items:
                    logger.warning(f"⚠️ Shopee returned empty items list from API")
                    continue
                
                # Parse each item
                for item in search_items:
                    # Get item_basic (main product info)
                    item_basic = item.get("item_basic", item)
                    
                    # Extract rating information
                    try:
                        # item_rating contains rating_star
                        item_rating_obj = item_basic.get("item_rating", {})
                        item_rating = float(item_rating_obj.get("rating_star", 0) if isinstance(item_rating_obj, dict) else 0)
                        
                        # Fallback ratings
                        shop_rating = float(item_basic.get("shop_rating", 0) or 0)
                        rating = float(item_basic.get("rating", 0) or 0)
                    except (ValueError, TypeError):
                        item_rating = shop_rating = rating = 0
                    
                    # Use highest rating available
                    max_rating = max(item_rating, shop_rating, rating)
                    
                    # Filter by rating (lenient - accept if no rating info)
                    if max_rating >= min_rating or max_rating == 0:
                        items.append(item_basic)
            
            # If no items from API, try fallback data
            if not items:
                logger.warning(f"⚠️ No items from Shopee API, trying fallback data")
                return await self._fallback_shopee_data(product_name, max_items, min_rating)
                    
            logger.info(f"✅ Scraped {len(items)} products from Shopee")
            return items
            
        except Exception as e:
            error_msg = str(e)
            if "exceed your remaining usage" in error_msg:
                logger.warning(f"⚠️ Apify credits exhausted for Shopee")
            elif "cookie" in error_msg.lower():
                logger.warning(f"⚠️ Shopee may require cookies for access")
            else:
                logger.error(f"❌ Shopee scrape error: {error_msg[:200]}")
            
            # Try fallback to pre-scraped data if available
            return await self._fallback_shopee_data(product_name, max_items, min_rating)
    
    async def _fallback_shopee_data(
        self,
        product_name: str,
        max_items: int,
        min_rating: float
    ) -> List[Dict[str, Any]]:
        """Fallback to pre-scraped Shopee supplier data"""
        try:
            from app.utils.shopee_data_loader import get_shopee_data_loader
            
            logger.info(f"💾 Using fallback Shopee data for: {product_name}")
            loader = get_shopee_data_loader()
            results = loader.search(product_name, limit=max_items)
            
            if results:
                logger.info(f"✅ Found {len(results)} suppliers from fallback data")
            else:
                logger.warning(f"⚠️ No fallback data found for: {product_name}")
            
            return results
        except Exception as e:
            logger.error(f"Fallback data loading failed: {str(e)}")
            return []
    
    async def _fallback_tokopedia_data(
        self,
        product_name: str,
        max_items: int,
        min_rating: float
    ) -> List[Dict[str, Any]]:
        """Fallback to dummy Tokopedia data"""
        logger.info(f"💾 Using dummy Tokopedia data for: {product_name}")
        
        # Generate dummy products based on search
        dummy_products = [
            {
                "name": f"Sepatu Sneakers Nike Air Force Premium Quality",
                "price": 450000,
                "rating": 4.8,
                "review_count": 1250,
                "total_sold": 3200,
                "shop_name": "Nike Official Store",
                "shop_location": "Jakarta Selatan",
                "url": "https://www.tokopedia.com/nike/sepatu-sneakers",
                "image_url": "https://images.tokopedia.net/img/cache/500-square/product.jpg",
                "is_official": True
            },
            {
                "name": f"Adidas Superstar Original Shoes - Putih",
                "price": 650000,
                "rating": 4.9,
                "review_count": 2100,
                "total_sold": 5400,
                "shop_name": "Adidas Official",
                "shop_location": "Jakarta Pusat",
                "url": "https://www.tokopedia.com/adidas/superstar",
                "image_url": "https://images.tokopedia.net/img/cache/500-square/product2.jpg",
                "is_official": True
            },
            {
                "name": f"Puma Suede Classic Sneakers Unisex",
                "price": 580000,
                "rating": 4.7,
                "review_count": 890,
                "total_sold": 2100,
                "shop_name": "Puma Store ID",
                "shop_location": "Bandung",
                "url": "https://www.tokopedia.com/puma/suede-classic",
                "image_url": "https://images.tokopedia.net/img/cache/500-square/product3.jpg",
                "is_official": True
            }
        ]
        
        return dummy_products[:max_items]
    
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
            logger.info(f"🔍 Scraping Lazada: {product_name}")
            
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
                # Filter by rating (Lazada uses multiple possible fields)
                try:
                    rating_score = float(item.get("rating_score", 0) or 0)
                    rating = float(item.get("rating", 0) or 0)
                    product_rating = float(item.get("product_rating", 0) or 0)
                except (ValueError, TypeError):
                    rating_score = rating = product_rating = 0
                
                # Use highest rating available
                max_rating = max(rating_score, rating, product_rating)
                
                # Accept if rating meets threshold or no rating info
                if max_rating >= min_rating or max_rating == 0:
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
                    
            logger.info(f"✅ Scraped {len(items)} products from Lazada")
            return items
            
        except Exception as e:
            error_msg = str(e)
            if "exceed your remaining usage" in error_msg:
                logger.warning(f"⚠️ Apify credits exhausted for Lazada - using fallback")
            else:
                logger.error(f"❌ Lazada scrape error: {error_msg}")
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
                location = item.get("shopLocation", "Indonesia")
                
                # Safely extract numeric fields
                def safe_float(val, default=0.0):
                    if isinstance(val, dict):
                        return float(val.get('value', val.get('amount', default)))
                    try:
                        return float(val) if val else default
                    except (ValueError, TypeError):
                        return default
                
                def safe_int(val, default=0):
                    if isinstance(val, dict):
                        return int(val.get('value', val.get('count', default)))
                    try:
                        return int(val) if val else default
                    except (ValueError, TypeError):
                        return default
                
                return Supplier(
                    name=item.get("sellerName", item.get("shopName", "Unknown")),
                    store_name=item.get("shopName", item.get("sellerName", "Unknown")),
                    marketplace="Tokopedia",
                    location=location,
                    city=location.split(',')[0] if ',' in location else location,
                    rating=safe_float(item.get("sellerRating", item.get("rating", 4.0)), 4.0),
                    product_name=item.get("name", item.get("productName", "Unknown Product")),
                    price=safe_float(item.get("price", 0)),
                    currency="IDR",
                    minimum_order=safe_int(item.get("minOrder", 1), 1),
                    stock_available=(safe_int(item.get("stock", 1), 1)) > 0,
                    url=item.get("url", item.get("productUrl", "")),
                    phone=item.get("phone", ""),
                    email=item.get("email", ""),
                    total_sold=safe_int(item.get("sold", item.get("totalSold", 0))),
                    review_count=safe_int(item.get("reviewCount", 0))
                )
            
            elif marketplace == "shopee":
                location = item.get("shopLocation", item.get("location", "Indonesia"))
                
                # Safely extract numeric fields
                def safe_float(val, default=0.0):
                    if isinstance(val, dict):
                        return float(val.get('value', val.get('amount', default)))
                    try:
                        return float(val) if val else default
                    except (ValueError, TypeError):
                        return default
                
                def safe_int(val, default=0):
                    if isinstance(val, dict):
                        return int(val.get('value', val.get('count', default)))
                    try:
                        return int(val) if val else default
                    except (ValueError, TypeError):
                        return default
                
                return Supplier(
                    name=item.get("shopName", item.get("shop_name", "Unknown")),
                    store_name=item.get("shopName", item.get("shop_name", "Unknown")),
                    marketplace="Shopee",
                    location=location,
                    city=location.split(',')[0] if ',' in location else location,
                    rating=safe_float(item.get("shopRating", item.get("rating", 4.5)), 4.5),
                    product_name=item.get("name", item.get("title", "Unknown Product")),
                    price=safe_float(item.get("price", 0)),
                    currency="IDR",
                    minimum_order=safe_int(item.get("minPurchase", item.get("min_purchase", 1)), 1),
                    stock_available=(safe_int(item.get("stock", 1), 1)) > 0,
                    url=item.get("url", item.get("product_url", "")),
                    phone=item.get("phone", ""),
                    email=item.get("email", ""),
                    total_sold=safe_int(item.get("sold", item.get("historical_sold", 0))),
                    review_count=safe_int(item.get("review_count", 0))
                )
            
            elif marketplace == "lazada":
                location = item.get("sellerLocation", item.get("location", "Indonesia"))
                
                # Safely extract numeric fields
                def safe_float(val, default=0.0):
                    if isinstance(val, dict):
                        return float(val.get('value', val.get('amount', default)))
                    try:
                        return float(val) if val else default
                    except (ValueError, TypeError):
                        return default
                
                def safe_int(val, default=0):
                    if isinstance(val, dict):
                        return int(val.get('value', val.get('count', default)))
                    try:
                        return int(val) if val else default
                    except (ValueError, TypeError):
                        return default
                
                return Supplier(
                    name=item.get("sellerName", item.get("seller_name", "Unknown")),
                    store_name=item.get("sellerName", item.get("seller_name", "Unknown")),
                    marketplace="Lazada",
                    location=location,
                    city=location.split(',')[0] if ',' in location else location,
                    rating=safe_float(item.get("sellerRating", item.get("rating", 4.0)), 4.0),
                    product_name=item.get("name", item.get("product_name", "Unknown Product")),
                    price=safe_float(item.get("price", 0)),
                    currency="IDR",
                    minimum_order=1,
                    stock_available=item.get("in_stock", True),
                    url=item.get("url", item.get("product_url", "")),
                    phone=item.get("phone", ""),
                    email=item.get("email", ""),
                    total_sold=safe_int(item.get("sold", 0)),
                    review_count=safe_int(item.get("review_count", 0))
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
