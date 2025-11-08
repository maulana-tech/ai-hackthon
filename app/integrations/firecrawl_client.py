import asyncio
from typing import List, Dict, Any, Optional
from firecrawl import FirecrawlApp
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class FirecrawlClient:
    def __init__(self):
        self.client = FirecrawlApp(api_key=settings.firecrawl_api_key)
        self.max_retries = settings.max_retries
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def scrape(
        self,
        url: str,
        formats: List[str] = None,
        actions: List[Dict[str, Any]] = None,
        extract_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Scrape a single URL with Firecrawl"""
        try:
            if formats is None:
                formats = ["markdown", "json"]
                
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
                
            logger.info(f"Scraping URL: {url}")
            result = self.client.scrape(url, **scrape_options)
            
            return result
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            raise
            
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
            result = self.client.crawl(url, **crawl_options)
            
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
                limit=limit,
                scrape_options={"formats": formats}
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
