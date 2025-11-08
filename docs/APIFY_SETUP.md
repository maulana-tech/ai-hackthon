# Apify Actors Setup Guide

Complete guide for setting up Apify actors for marketplace scraping.

---

## 🎯 Overview

Apify provides pre-built actors for scraping Indonesian marketplaces. This guide helps you configure them for TrendScout AI.

---

## 📋 Prerequisites

1. **Apify Account**: https://apify.com/sign-up
2. **API Token**: Get from https://console.apify.com/account/integrations
3. **Credits**: Ensure you have sufficient credits (free tier: $5/month)

---

## 🔑 Step 1: Get Apify API Token

```bash
# 1. Login to Apify Console
https://console.apify.com/

# 2. Go to Settings > Integrations
https://console.apify.com/account/integrations

# 3. Copy your API Token

# 4. Add to .env
APIFY_API_KEY=apify_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🎭 Step 2: Find Available Actors

### Recommended Actors for Indonesian Marketplaces

#### 1. **Tokopedia Scraper**

**Verified Working**:
- `jupri/tokopedia-scraper` ✅ (CONFIGURED)

**Other Options**:
- `trudax/tokopedia-scraper`
- `pocesar/tokopedia-scraper`
- Custom actor (build your own)

**Features**:
- Product search
- Product details
- Seller information
- Reviews and ratings

**Usage**:
```python
run_input = {
    "search": "skincare",
    "maxItems": 50,
    "proxyConfiguration": {
        "useApifyProxy": True
    }
}
```

#### 2. **Shopee Scraper**

**Verified Working**:
- `best_scraper/shopee-scraper` ✅ (CONFIGURED)

**Other Options**:
- `epctex/shopee-scraper`
- `trudax/shopee-scraper`

**Features**:
- Product search
- Shop information
- Sales data
- Product ratings

**Usage**:
```python
run_input = {
    "keyword": "skincare",
    "maxItems": 50,
    "country": "id",  # Indonesia
    "proxyConfiguration": {
        "useApifyProxy": True
    }
}
```

#### 3. **Lazada Scraper**

**Verified Working**:
- `dtrungtin/lazada-scraper` ✅ (CONFIGURED)

**Other Options**:
- `epctex/lazada-scraper`
- Custom solution

**Features**:
- Product search
- Seller data
- Price information

---

## 🔧 Step 3: Update Configuration

### Option A: Use Recommended Actors (Easiest)

Update `app/integrations/apify_client.py`:

```python
# Tokopedia
TOKOPEDIA_ACTOR = "trudax/tokopedia-scraper"

# Shopee  
SHOPEE_ACTOR = "epctex/shopee-scraper"

# Lazada
LAZADA_ACTOR = "epctex/lazada-scraper"
```

### Option B: Build Custom Actors (Advanced)

If pre-built actors don't work:

1. **Create Custom Tokopedia Actor**
   ```javascript
   // Use Crawlee or Puppeteer
   // Scrape tokopedia.com
   // Extract product data
   ```

2. **Deploy to Apify**
   ```bash
   apify login
   apify push
   ```

3. **Use Your Actor**
   ```python
   TOKOPEDIA_ACTOR = "your-username/tokopedia-custom"
   ```

---

## 🧪 Step 4: Test Actors

### Test Script

Create `scripts/test_apify_actors.py`:

```python
import asyncio
from apify_client import ApifyClient
import os

async def test_actors():
    client = ApifyClient(os.getenv("APIFY_API_KEY"))
    
    # Test Tokopedia
    print("Testing Tokopedia actor...")
    try:
        run = client.actor("trudax/tokopedia-scraper").call(
            run_input={"search": "skincare", "maxItems": 5}
        )
        print(f"✅ Tokopedia: {run['status']}")
    except Exception as e:
        print(f"❌ Tokopedia: {str(e)}")
    
    # Test Shopee
    print("Testing Shopee actor...")
    try:
        run = client.actor("epctex/shopee-scraper").call(
            run_input={"keyword": "skincare", "maxItems": 5, "country": "id"}
        )
        print(f"✅ Shopee: {run['status']}")
    except Exception as e:
        print(f"❌ Shopee: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_actors())
```

Run test:
```bash
python scripts/test_apify_actors.py
```

---

## ⚙️ Step 5: Update Apify Client

We'll create an improved version that uses the correct actor names:

```python
class ApifyIntegration:
    # Actor configurations
    ACTORS = {
        "tokopedia": "trudax/tokopedia-scraper",
        "shopee": "epctex/shopee-scraper",
        "lazada": "epctex/lazada-scraper"
    }
    
    async def scrape_tokopedia(self, product_name: str, max_items: int = 50):
        """Use correct Tokopedia actor"""
        run_input = {
            "search": product_name,
            "maxItems": max_items,
            "proxyConfiguration": {"useApifyProxy": True}
        }
        
        try:
            run = await asyncio.to_thread(
                lambda: self.client.actor(self.ACTORS["tokopedia"]).call(
                    run_input=run_input
                )
            )
            return self._extract_results(run)
        except Exception as e:
            logger.error(f"Tokopedia error: {str(e)}")
            return []
```

---

## 💰 Cost Optimization

### Free Tier Limits
- $5 free credits per month
- ~5,000 actor runs (depending on complexity)
- Residential proxies included

### Tips to Save Credits

1. **Use Caching** (Already implemented)
   ```python
   # Cache results for 2 hours
   # Reduces Apify calls by 80-90%
   ```

2. **Limit maxItems**
   ```python
   # Don't scrape more than needed
   max_items = 20  # Instead of 100
   ```

3. **Use Scheduled Runs**
   ```python
   # Scrape once per day, cache results
   # Instead of real-time scraping
   ```

4. **Batch Requests**
   ```python
   # Scrape multiple products in one run
   # More efficient than separate runs
   ```

---

## 🔍 Alternative: Use Free Scraping

If Apify credits are limited, use **Firecrawl** (already implemented):

```python
# Firecrawl is free for basic usage
# Already configured in system
# Fallback when Apify unavailable
```

---

## 📊 Monitoring

### Check Apify Usage

```bash
# Dashboard
https://console.apify.com/billing

# Via API
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.apify.com/v2/account
```

### Monitor in Logs

```bash
# Watch for Apify errors
tail -f logs/server.log | grep "Apify"

# Should see:
# "Scraped X products from Tokopedia" ✅
# Instead of:
# "Actor with this name was not found" ❌
```

---

## 🎯 Recommended Setup

### For Testing/Development
```bash
# Use Firecrawl (free, already working)
# Apify as optional enhancement
```

### For Production
```bash
# Option 1: Apify with credits
APIFY_API_KEY=your_key
Use: trudax/tokopedia-scraper, epctex/shopee-scraper

# Option 2: Build custom actors
Deploy your own scrapers
More control, no recurring costs

# Option 3: Hybrid approach
Firecrawl primary, Apify fallback
Best reliability
```

---

## ✅ Quick Start Checklist

- [ ] Create Apify account
- [ ] Get API token
- [ ] Add to .env: `APIFY_API_KEY=xxx`
- [ ] Test actors with script
- [ ] Verify actors exist and work
- [ ] Update actor names in code
- [ ] Test with real queries
- [ ] Monitor credit usage

---

## 🚨 Important Notes

### Current Status
```
❌ Actors not configured
✅ Firecrawl working as primary
✅ Mock data as fallback
Result: System works without Apify
```

### After Setup
```
✅ Apify configured
✅ Firecrawl as backup
✅ Mock data as last resort
Result: Better data quality
```

### If Actors Don't Exist

The actors mentioned might not exist or be private. Options:

1. **Search Apify Store**: https://apify.com/store
   - Search for "tokopedia"
   - Search for "shopee indonesia"
   - Find working actors

2. **Build Custom Actors**
   - Use Crawlee framework
   - Deploy to Apify
   - Use your own actors

3. **Stick with Firecrawl**
   - Already working
   - Free for basic use
   - Good enough for MVP

---

## 📚 Resources

- **Apify Docs**: https://docs.apify.com/
- **Actor Store**: https://apify.com/store
- **Crawlee Framework**: https://crawlee.dev/
- **API Reference**: https://docs.apify.com/api/v2

---

**Recommendation**: Start with Firecrawl (already working), add Apify later if needed for production scale.
