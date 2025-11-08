# Apify API Integration Guide

## Overview

Apify adalah platform web scraping dan automation yang powerful dengan 1500+ ready-made scrapers (Actors). TrendScout dapat menggunakan Apify untuk scraping marketplace Indonesia seperti Tokopedia, Shopee, Lazada, dan lainnya.

## 🎯 Kenapa Apify?

### Keunggulan:
- ✅ **1500+ Ready Actors** - Pre-built scrapers untuk berbagai website
- ✅ **No Blocking** - Handle captcha, rate limiting, anti-bot
- ✅ **Scalable** - Parallel scraping dengan proxy rotation
- ✅ **Structured Data** - Output langsung JSON/CSV
- ✅ **Reliable** - 99.9% uptime

### Use Cases di TrendScout:
1. **Scrape Tokopedia** - Product details, seller info, reviews
2. **Scrape Shopee** - Prices, stock, seller ratings
3. **Scrape Lazada** - Product listings, categories
4. **Scrape Instagram** - Trending products, hashtag analysis
5. **Scrape TikTok** - Viral products, shop analytics

## 🔧 Setup

### 1. Get API Key

1. Sign up: https://console.apify.com/sign-up
2. Go to Settings → Integrations → API tokens
3. Copy your API token
4. Add to `.env`:

```env
APIFY_API_KEY=apify_api_xxxxxxxxxxxxxxxxxxxxxxxx
```

### 2. Install Apify Client

Already installed in requirements.txt, but if needed:

```bash
uv pip install apify-client
```

## 📊 Recommended Apify Actors for TrendScout

### 1. **Tokopedia Scraper**

**Actor:** `apify/tokopedia-scraper`

**Features:**
- Product details (name, price, description)
- Seller information (name, location, rating)
- Reviews and ratings
- Stock availability
- Product images

**Use Case:** Find suppliers on Tokopedia

**Cost:** ~$0.10 per 1000 products

### 2. **Shopee Scraper**

**Actor:** `epctex/shopee-scraper`

**Features:**
- Product listings
- Shop details
- Seller ratings
- Price history
- Category scraping

**Use Case:** Compare suppliers across Shopee

**Cost:** ~$0.15 per 1000 products

### 3. **Lazada Scraper**

**Actor:** `apify/lazada-scraper`

**Features:**
- Product search
- Seller information
- Flash sale products
- Category browsing

**Use Case:** Find Lazada suppliers

**Cost:** ~$0.10 per 1000 products

### 4. **Instagram Scraper**

**Actor:** `apify/instagram-scraper`

**Features:**
- Profile scraping
- Hashtag posts
- Post engagement
- Comments

**Use Case:** Trend analysis from Instagram

**Cost:** ~$0.20 per 1000 posts

### 5. **TikTok Scraper**

**Actor:** `clockworks/tiktok-scraper`

**Features:**
- Trending hashtags
- User profiles
- Video details
- Shop products

**Use Case:** Viral product detection

**Cost:** ~$0.25 per 1000 videos

### 6. **Google Search Scraper**

**Actor:** `apify/google-search-scraper`

**Features:**
- Search results
- Shopping results
- Related searches
- Trending topics

**Use Case:** Market research

**Cost:** ~$0.05 per 100 searches

## 💻 Implementation

### Create Apify Client

```python
# app/integrations/apify_client.py

import asyncio
import logging
from typing import List, Dict, Any, Optional
from apify_client import ApifyClient

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ApifyIntegration:
    """Apify API client for web scraping"""
    
    def __init__(self):
        self.client = ApifyClient(settings.apify_api_key)
        
    async def scrape_tokopedia(
        self,
        product_name: str,
        max_items: int = 50
    ) -> List[Dict[str, Any]]:
        """Scrape Tokopedia for products"""
        try:
            logger.info(f"Scraping Tokopedia: {product_name}")
            
            run_input = {
                "searchQuery": product_name,
                "maxItems": max_items,
                "proxyConfiguration": {
                    "useApifyProxy": True,
                    "apifyProxyGroups": ["RESIDENTIAL"]
                }
            }
            
            # Run actor
            run = self.client.actor("apify/tokopedia-scraper").call(run_input=run_input)
            
            # Get results
            items = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                items.append(item)
                
            logger.info(f"Scraped {len(items)} products from Tokopedia")
            return items
            
        except Exception as e:
            logger.error(f"Tokopedia scrape error: {str(e)}")
            return []
    
    async def scrape_shopee(
        self,
        product_name: str,
        max_items: int = 50
    ) -> List[Dict[str, Any]]:
        """Scrape Shopee for products"""
        try:
            logger.info(f"Scraping Shopee: {product_name}")
            
            run_input = {
                "keyword": product_name,
                "maxItems": max_items,
                "country": "id",  # Indonesia
            }
            
            run = self.client.actor("epctex/shopee-scraper").call(run_input=run_input)
            
            items = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                items.append(item)
                
            logger.info(f"Scraped {len(items)} products from Shopee")
            return items
            
        except Exception as e:
            logger.error(f"Shopee scrape error: {str(e)}")
            return []
    
    async def scrape_lazada(
        self,
        product_name: str,
        max_items: int = 50
    ) -> List[Dict[str, Any]]:
        """Scrape Lazada for products"""
        try:
            logger.info(f"Scraping Lazada: {product_name}")
            
            run_input = {
                "search": product_name,
                "maxItems": max_items,
                "country": "id"
            }
            
            run = self.client.actor("apify/lazada-scraper").call(run_input=run_input)
            
            items = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                items.append(item)
                
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
        """Scrape Instagram hashtag for trend analysis"""
        try:
            logger.info(f"Scraping Instagram: #{hashtag}")
            
            run_input = {
                "hashtags": [hashtag],
                "resultsLimit": max_posts
            }
            
            run = self.client.actor("apify/instagram-scraper").call(run_input=run_input)
            
            posts = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
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
        """Scrape TikTok hashtag for viral products"""
        try:
            logger.info(f"Scraping TikTok: #{hashtag}")
            
            run_input = {
                "hashtags": [hashtag],
                "resultsPerPage": max_videos
            }
            
            run = self.client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
            
            videos = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                videos.append(item)
                
            logger.info(f"Scraped {len(videos)} TikTok videos")
            return videos
            
        except Exception as e:
            logger.error(f"TikTok scrape error: {str(e)}")
            return []
    
    async def scrape_all_marketplaces(
        self,
        product_name: str,
        max_items_per_marketplace: int = 20
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape all Indonesian marketplaces in parallel"""
        try:
            logger.info(f"Scraping all marketplaces: {product_name}")
            
            # Run all scrapers in parallel
            results = await asyncio.gather(
                self.scrape_tokopedia(product_name, max_items_per_marketplace),
                self.scrape_shopee(product_name, max_items_per_marketplace),
                self.scrape_lazada(product_name, max_items_per_marketplace),
                return_exceptions=True
            )
            
            tokopedia, shopee, lazada = results
            
            return {
                "tokopedia": tokopedia if isinstance(tokopedia, list) else [],
                "shopee": shopee if isinstance(shopee, list) else [],
                "lazada": lazada if isinstance(lazada, list) else []
            }
            
        except Exception as e:
            logger.error(f"Multi-marketplace scrape error: {str(e)}")
            return {"tokopedia": [], "shopee": [], "lazada": []}
```

### Usage Example

```python
from app.integrations.apify_client import ApifyIntegration

# Initialize
apify = ApifyIntegration()

# Scrape Tokopedia
products = await apify.scrape_tokopedia("macrame wall hanging", max_items=50)

# Scrape all marketplaces
all_products = await apify.scrape_all_marketplaces("LED face mask", max_items_per_marketplace=20)

# Analyze Instagram trends
posts = await apify.scrape_instagram_hashtag("skincare", max_posts=100)
```

## 💰 Pricing

### Free Tier:
- $5 free credits per month
- ~500-1000 products/month
- Good for testing

### Paid Plans:
- **Starter**: $49/month - 100,000 operations
- **Team**: $149/month - 500,000 operations
- **Business**: $499/month - 2M operations

### Cost Estimation for TrendScout:

**Scenario 1: Low Volume (50 queries/day)**
- 50 queries × 20 products × $0.10/1000 = $0.10/day
- Monthly: ~$3
- **Plan: Free tier** ✅

**Scenario 2: Medium Volume (200 queries/day)**
- 200 queries × 20 products × $0.10/1000 = $0.40/day
- Monthly: ~$12
- **Plan: Starter $49** ✅

**Scenario 3: High Volume (1000 queries/day)**
- 1000 queries × 20 products × $0.10/1000 = $2/day
- Monthly: ~$60
- **Plan: Team $149** ✅

## 🎯 Integration with Supplier Scout Agent

Update `app/agents/supplier_scout.py`:

```python
from app.integrations.apify_client import ApifyIntegration

class SupplierScoutAgent:
    def __init__(self):
        self.firecrawl = FirecrawlClient()
        self.apify = ApifyIntegration()  # ✅ Add Apify
        self.name = "Supplier Scout Agent"
    
    async def find_suppliers(
        self,
        product_name: str,
        location: Optional[str] = None,
        min_rating: float = 4.0,
        limit: int = 5,
        use_apify: bool = True  # ✅ Add flag
    ) -> List[Supplier]:
        """Find suppliers with Apify + Firecrawl"""
        
        if use_apify:
            # Use Apify for faster, more reliable scraping
            apify_results = await self.apify.scrape_all_marketplaces(product_name)
            
            suppliers = []
            
            # Parse Tokopedia results
            for item in apify_results["tokopedia"]:
                supplier = self._parse_tokopedia_apify(item)
                suppliers.append(supplier)
            
            # Parse Shopee results
            for item in apify_results["shopee"]:
                supplier = self._parse_shopee_apify(item)
                suppliers.append(supplier)
            
            # Parse Lazada results
            for item in apify_results["lazada"]:
                supplier = self._parse_lazada_apify(item)
                suppliers.append(supplier)
        else:
            # Fallback to Firecrawl
            suppliers = await self._search_with_firecrawl(product_name)
        
        return self._rank_and_filter(suppliers, limit)
```

## 📊 Comparison: Apify vs Firecrawl

| Feature | Apify | Firecrawl |
|---------|-------|-----------|
| **Speed** | ⚡⚡⚡ Fast (optimized actors) | ⚡⚡ Medium |
| **Reliability** | ✅✅✅ Very High | ✅✅ High |
| **Anti-bot Handling** | ✅ Built-in | ⚠️ Manual |
| **Structured Data** | ✅ JSON ready | ⚠️ Need parsing |
| **Coverage** | 1500+ sites | Any site |
| **Cost** | $$ Per operation | $$$ Per page |
| **Best For** | Known marketplaces | Custom sites |

**Recommendation**: 
- **Use Apify** for Tokopedia, Shopee, Lazada (faster, reliable)
- **Use Firecrawl** for custom sites like Indonetwork (flexible)

## 🚀 Quick Start

### 1. Add to requirements.txt

```txt
apify-client==1.8.0
```

Install:
```bash
uv pip install apify-client
```

### 2. Create client file

Save the implementation above as:
```
app/integrations/apify_client.py
```

### 3. Update config

Already in `app/config.py`:
```python
apify_api_key: str
```

### 4. Add to .env

```env
APIFY_API_KEY=apify_api_xxxxxxxxxxxxxxxx
```

### 5. Test

```python
# Test script
from app.integrations.apify_client import ApifyIntegration

async def test():
    apify = ApifyIntegration()
    
    # Test Tokopedia
    products = await apify.scrape_tokopedia("macrame", max_items=10)
    print(f"Found {len(products)} products")
    
    for p in products[:3]:
        print(f"- {p.get('name')} - Rp{p.get('price')}")

# Run
import asyncio
asyncio.run(test())
```

## 🎓 Best Practices

### 1. Use Proxies
```python
run_input = {
    "proxyConfiguration": {
        "useApifyProxy": True,
        "apifyProxyGroups": ["RESIDENTIAL"]  # More reliable
    }
}
```

### 2. Handle Rate Limits
```python
# Add delays between scrapes
await asyncio.sleep(1)
```

### 3. Cache Results
```python
# Cache for 24 hours
import redis
cache = redis.Redis()
cache.setex(f"apify:{product_name}", 86400, json.dumps(results))
```

### 4. Error Handling
```python
try:
    results = await apify.scrape_tokopedia(product)
except Exception as e:
    logger.error(f"Apify error: {e}")
    # Fallback to Firecrawl
    results = await firecrawl.scrape(url)
```

### 5. Monitor Costs
```python
# Check usage
usage = client.user().usage()
print(f"Credits used: ${usage['usage']['monthUsage']}")
```

## 📚 Resources

- **Apify Documentation**: https://docs.apify.com/
- **Actor Store**: https://apify.com/store
- **API Reference**: https://docs.apify.com/api/v2
- **Python Client**: https://docs.apify.com/api/client/python
- **Pricing**: https://apify.com/pricing

## ✅ Summary

**Apify API yang digunakan di TrendScout:**

1. ✅ **Tokopedia Scraper** - Find suppliers
2. ✅ **Shopee Scraper** - Compare prices
3. ✅ **Lazada Scraper** - More options
4. ✅ **Instagram Scraper** - Trend analysis
5. ✅ **TikTok Scraper** - Viral products

**Benefits:**
- Faster than custom scraping
- No blocking issues
- Structured JSON output
- Scalable and reliable

**Cost:** ~$5-50/month depending on usage

Ready to implement! 🚀
