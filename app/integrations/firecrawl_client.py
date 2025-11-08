import asyncio
from typing import List, Dict, Any, Optional
from firecrawl import FirecrawlApp
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
import hashlib
import json

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Simple in-memory cache (for session)
_cache = {}
_cache_ttl = 7200  # 2 hours

class FirecrawlClient:
    def __init__(self):
        self.client = FirecrawlApp(api_key=settings.firecrawl_api_key)
        self.max_retries = settings.max_retries
        self.request_count = 0
        self.max_requests_per_minute = 10
        self.last_request_time = 0
    
    def _get_cache_key(self, url: str, params: Dict = None) -> str:
        """Generate cache key"""
        key_data = {'url': url, 'params': params}
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get from in-memory cache"""
        import time
        if cache_key in _cache:
            cached_data, timestamp = _cache[cache_key]
            if time.time() - timestamp < _cache_ttl:
                logger.info(f"✅ Cache hit for key: {cache_key[:10]}...")
                return cached_data
            else:
                del _cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save to in-memory cache"""
        import time
        _cache[cache_key] = (data, time.time())
        logger.info(f"💾 Cached result for key: {cache_key[:10]}...")
    
    async def _rate_limit(self):
        """Simple rate limiting"""
        import time
        now = time.time()
        if now - self.last_request_time < 60:
            if self.request_count >= self.max_requests_per_minute:
                wait_time = 60 - (now - self.last_request_time)
                logger.warning(f"⏳ Rate limit: waiting {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.last_request_time = time.time()
        else:
            self.request_count = 0
            self.last_request_time = now
        
        self.request_count += 1
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def scrape(
        self,
        url: str,
        formats: List[str] = None,
        actions: List[Dict[str, Any]] = None,
        extract_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Scrape a single URL with Firecrawl (with caching)"""
        try:
            if formats is None:
                formats = ["markdown", "json"]
            
            # Generate cache key
            cache_params = {
                'formats': formats,
                'actions': actions,
                'schema': extract_schema
            }
            cache_key = self._get_cache_key(url, cache_params)
            
            # Check cache first
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                return cached_result
            
            # Apply rate limiting
            await self._rate_limit()
                
            scrape_options = {
                "formats": formats,
            }
            
            if actions:
                scrape_options["actions"] = actions
                
            if extract_schema:
                scrape_options["formats"] = [{
                    "type": "json",
                    "schema": extract_schema
                }]
                
            logger.info(f"🔍 Scraping URL: {url}")
            result = self.client.scrape_url(url, params=scrape_options)
            
            # Cache the result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            # Return empty result instead of raising
            return {}
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def crawl(
        self,
        url: str,
        limit: int = 10,
        formats: List[str] = None,
        exclude_paths: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Crawl a website with Firecrawl"""
        try:
            if formats is None:
                formats = ["markdown", "json"]
                
            crawl_options = {
                "limit": limit,
                "formats": formats,
            }
            
            if exclude_paths:
                crawl_options["excludePaths"] = exclude_paths
                
            logger.info(f"Crawling URL: {url} with limit: {limit}")
            result = self.client.crawl_url(url, params=crawl_options)
            
            return result
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            raise
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search(
        self,
        query: str,
        limit: int = 5,
        formats: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Search the web with Firecrawl"""
        try:
            if formats is None:
                formats = ["markdown"]
                
            logger.info(f"Searching: {query} with limit: {limit}")
            result = self.client.search(
                query,
                params={
                    "limit": limit,
                    "scrapeOptions": {"formats": formats}
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching {query}: {str(e)}")
            raise
            
    async def scrape_with_actions(
        self,
        url: str,
        actions: List[Dict[str, Any]],
        formats: List[str] = None
    ) -> Dict[str, Any]:
        """Scrape with browser actions (click, scroll, etc)"""
        return await self.scrape(url, formats=formats, actions=actions)
        
    async def extract_structured_data(
        self,
        url: str,
        schema: Dict[str, Any],
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract structured data using schema or prompt"""
        if prompt:
            return await self.scrape(
                url,
                formats=[{
                    "type": "json",
                    "prompt": prompt
                }]
            )
        else:
            return await self.scrape(
                url,
                extract_schema=schema
            )
