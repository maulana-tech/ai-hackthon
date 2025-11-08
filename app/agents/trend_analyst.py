import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
import json
from pytrends.request import TrendReq
import httpx

from app.models.schemas import TrendingProduct
from app.integrations.firecrawl_client import FirecrawlClient
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class TrendAnalystAgent:
    """Agent to analyze global product trends using multiple sources"""
    
    def __init__(self):
        self.firecrawl = FirecrawlClient()
        self.pytrends = TrendReq(hl='en-US', tz=360)
        self.name = "Trend Analyst Agent"
        
    async def analyze_trends(
        self,
        query: str,
        region: str = "global",
        limit: int = 3
    ) -> List[TrendingProduct]:
        """Main method to analyze trends from multiple sources"""
        logger.info(f"Starting trend analysis for: {query}")
        
        tasks = [
            self._scrape_google_trends(query, region),
            self._scrape_tiktok_creative_center(query),
            self._scrape_amazon_best_sellers(query),
            self._search_trending_products(query)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_products = []
        for result in results:
            if isinstance(result, list):
                all_products.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Task failed: {str(result)}")
                
        ranked_products = self._rank_and_filter(all_products, limit)
        
        return ranked_products
        
    async def _scrape_google_trends(self, query: str, region: str) -> List[TrendingProduct]:
        """Scrape Google Trends for trending products"""
        try:
            logger.info(f"Scraping Google Trends for: {query}")
            
            await asyncio.to_thread(
                self.pytrends.build_payload,
                [query],
                cat=0,
                timeframe='today 3-m',
                geo='' if region == 'global' else region
            )
            
            interest_over_time = await asyncio.to_thread(
                self.pytrends.interest_over_time
            )
            
            related_queries = await asyncio.to_thread(
                self.pytrends.related_queries
            )
            
            products = []
            
            if not interest_over_time.empty:
                avg_interest = interest_over_time[query].mean()
                max_interest = interest_over_time[query].max()
                
                if 'rising' in related_queries[query]:
                    rising = related_queries[query]['rising']
                    if rising is not None and not rising.empty:
                        for idx, row in rising.head(3).iterrows():
                            product = TrendingProduct(
                                name=row['query'],
                                category=self._infer_category(row['query']),
                                trend_score=float(row.get('value', avg_interest)),
                                growth_percentage=float(row.get('value', 0)),
                                search_volume=int(max_interest * 1000),
                                region=region,
                                platform="Google Trends",
                                keywords=[query, row['query']]
                            )
                            products.append(product)
                            
            return products
            
        except Exception as e:
            logger.error(f"Error scraping Google Trends: {str(e)}")
            return []
            
    async def _scrape_tiktok_creative_center(self, query: str) -> List[TrendingProduct]:
        """Scrape TikTok Creative Center for trending products"""
        try:
            logger.info(f"Scraping TikTok Creative Center for: {query}")
            
            url = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"
            
            result = await self.firecrawl.scrape(
                url,
                formats=[{
                    "type": "json",
                    "prompt": f"Extract trending hashtags and products related to {query}. Include engagement metrics."
                }]
            )
            
            products = []
            
            if result and 'data' in result:
                data = result['data']
                if 'json' in data:
                    json_data = data['json']
                    
                    if isinstance(json_data, dict) and 'trending_products' in json_data:
                        for item in json_data['trending_products'][:3]:
                            product = TrendingProduct(
                                name=item.get('name', query),
                                category=item.get('category', 'general'),
                                trend_score=float(item.get('engagement_score', 75.0)),
                                growth_percentage=float(item.get('growth', 50.0)),
                                search_volume=int(item.get('views', 100000)),
                                region="global",
                                platform="TikTok",
                                description=item.get('description'),
                                keywords=[query]
                            )
                            products.append(product)
                            
            return products
            
        except Exception as e:
            logger.error(f"Error scraping TikTok: {str(e)}")
            return []
            
    async def _scrape_amazon_best_sellers(self, query: str) -> List[TrendingProduct]:
        """Scrape Amazon Best Sellers"""
        try:
            logger.info(f"Scraping Amazon Best Sellers for: {query}")
            
            search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
            
            result = await self.firecrawl.scrape(
                search_url,
                formats=[{
                    "type": "json",
                    "prompt": f"Extract product names, prices, ratings, and popularity indicators for products matching {query}"
                }]
            )
            
            products = []
            
            if result and 'data' in result:
                data = result['data']
                if 'json' in data:
                    json_data = data['json']
                    
                    if isinstance(json_data, dict) and 'products' in json_data:
                        for item in json_data['products'][:3]:
                            product = TrendingProduct(
                                name=item.get('name', query),
                                category=item.get('category', 'general'),
                                trend_score=float(item.get('rating', 4.0) * 20),
                                growth_percentage=45.0,
                                search_volume=50000,
                                region="US",
                                platform="Amazon",
                                description=item.get('description'),
                                price_range=item.get('price'),
                                keywords=[query]
                            )
                            products.append(product)
                            
            return products
            
        except Exception as e:
            logger.error(f"Error scraping Amazon: {str(e)}")
            return []
            
    async def _search_trending_products(self, query: str) -> List[TrendingProduct]:
        """Use Firecrawl search to find trending products"""
        try:
            logger.info(f"Searching for trending products: {query}")
            
            search_query = f"trending {query} products 2024"
            result = await self.firecrawl.search(
                search_query,
                limit=5,
                formats=["markdown"]
            )
            
            products = []
            
            if result and 'data' in result:
                for item in result['data'][:2]:
                    product = TrendingProduct(
                        name=query.title(),
                        category=self._infer_category(query),
                        trend_score=70.0,
                        growth_percentage=40.0,
                        search_volume=30000,
                        region="global",
                        platform="Web Search",
                        description=item.get('description', ''),
                        keywords=[query]
                    )
                    products.append(product)
                    
            return products
            
        except Exception as e:
            logger.error(f"Error searching trending products: {str(e)}")
            return []
            
    def _rank_and_filter(self, products: List[TrendingProduct], limit: int) -> List[TrendingProduct]:
        """Rank products by trend score and filter top results"""
        
        unique_products = {}
        for product in products:
            key = product.name.lower()
            if key not in unique_products or product.trend_score > unique_products[key].trend_score:
                unique_products[key] = product
                
        sorted_products = sorted(
            unique_products.values(),
            key=lambda x: x.trend_score,
            reverse=True
        )
        
        return sorted_products[:limit]
        
    def _infer_category(self, query: str) -> str:
        """Infer product category from query"""
        category_keywords = {
            'electronics': ['phone', 'laptop', 'gadget', 'tech', 'smart', 'device'],
            'fashion': ['clothing', 'fashion', 'apparel', 'wear', 'shoes', 'accessories'],
            'beauty': ['skincare', 'makeup', 'beauty', 'cosmetic', 'serum', 'cream'],
            'home': ['home', 'decor', 'furniture', 'kitchen', 'living'],
            'health': ['fitness', 'health', 'wellness', 'supplement', 'vitamin'],
            'toys': ['toy', 'game', 'kids', 'children', 'play']
        }
        
        query_lower = query.lower()
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
                
        return 'general'
        
    async def generate_analysis_summary(self, products: List[TrendingProduct]) -> str:
        """Generate a summary of trend analysis"""
        if not products:
            return "No trending products found for your query."
            
        summary = f"Found {len(products)} trending products:\n\n"
        
        for i, product in enumerate(products, 1):
            summary += f"{i}. **{product.name}** ({product.category})\n"
            summary += f"   - Platform: {product.platform}\n"
            summary += f"   - Trend Score: {product.trend_score:.1f}/100\n"
            summary += f"   - Growth: +{product.growth_percentage:.1f}%\n"
            summary += f"   - Search Volume: {product.search_volume:,}\n\n"
            
        return summary
