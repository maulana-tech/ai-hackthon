#!/usr/bin/env python3
"""
Real Scraping Test - TrendScout Supplier Connector

This script performs actual scraping with real data from:
1. Firecrawl - For Indonetwork B2B suppliers
2. Apify - For Tokopedia, Shopee, Lazada (if API key available)

Usage:
    python run_real_scraping.py
"""

import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path

from app.config import get_settings
from app.agents.supplier_scout import SupplierScoutAgent
from app.integrations.firecrawl_client import FirecrawlClient
from app.integrations.apify_client import ApifyIntegration

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
settings = get_settings()


def save_results(data: dict, filename: str):
    """Save scraping results to JSON file"""
    output_dir = Path("./data/scraping_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = output_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"✅ Results saved to: {filepath}")
    return filepath


async def test_firecrawl_indonetwork():
    """Test Firecrawl scraping on Indonetwork"""
    print("\n" + "="*60)
    print("🔥 Test 1: Firecrawl - Indonetwork B2B Scraping")
    print("="*60)
    
    if not settings.firecrawl_api_key or settings.firecrawl_api_key == "fc-YOUR-API-KEY":
        print("❌ Firecrawl API key not configured")
        print("   Set FIRECRAWL_API_KEY in .env file")
        return None
    
    try:
        firecrawl = FirecrawlClient()
        
        # Test scraping Indonetwork
        product = "macrame"
        print(f"\n🔍 Searching Indonetwork for: {product}")
        
        url = f"https://www.indonetwork.co.id/search?q={product}"
        
        print(f"📡 Scraping: {url}")
        print("⏳ Please wait (may take 10-30 seconds)...")
        
        result = await firecrawl.scrape(
            url=url,
            formats=["markdown", "json"]
        )
        
        if result:
            print(f"\n✅ Scraping successful!")
            print(f"   Data structure: {list(result.keys())}")
            
            # Save raw result
            filepath = save_results(result, "indonetwork_raw")
            
            # Display sample
            if 'data' in result and 'markdown' in result['data']:
                markdown = result['data']['markdown']
                print(f"\n📄 Sample content (first 500 chars):")
                print("-" * 60)
                print(markdown[:500])
                print("-" * 60)
            
            return result
        else:
            print("❌ No data returned")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"Firecrawl error: {str(e)}", exc_info=True)
        return None


async def test_apify_tokopedia():
    """Test Apify scraping on Tokopedia"""
    print("\n" + "="*60)
    print("🕷️  Test 2: Apify - Tokopedia Scraping")
    print("="*60)
    
    if not settings.apify_api_key or settings.apify_api_key == "your-apify-api-key":
        print("❌ Apify API key not configured")
        print("   Set APIFY_API_KEY in .env file")
        print("   Get free key at: https://console.apify.com")
        return None
    
    try:
        apify = ApifyIntegration()
        
        product = "macrame"
        print(f"\n🔍 Searching Tokopedia for: {product}")
        print("⏳ Please wait (Apify processing, ~30-60 seconds)...")
        
        products = await apify.scrape_tokopedia(
            product_name=product,
            max_items=5,
            min_rating=4.0
        )
        
        if products:
            print(f"\n✅ Found {len(products)} products!")
            
            # Save results
            filepath = save_results({"products": products}, "tokopedia_products")
            
            # Display samples
            print(f"\n📦 Sample Products:")
            print("-" * 60)
            for i, p in enumerate(products[:3], 1):
                print(f"{i}. {p.get('name', 'N/A')}")
                print(f"   Price: Rp{p.get('price', 0):,}")
                print(f"   Seller: {p.get('sellerName', 'N/A')}")
                print(f"   Rating: {p.get('sellerRating', 0)}/5.0")
                print(f"   Location: {p.get('shopLocation', 'N/A')}")
                print()
            print("-" * 60)
            
            return products
        else:
            print("❌ No products found")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"Apify error: {str(e)}", exc_info=True)
        return None


async def test_supplier_scout_agent():
    """Test full Supplier Scout Agent with real scraping"""
    print("\n" + "="*60)
    print("🤖 Test 3: Supplier Scout Agent - Full Workflow")
    print("="*60)
    
    try:
        agent = SupplierScoutAgent()
        
        product = "macrame wall hanging"
        print(f"\n🔍 Finding suppliers for: {product}")
        print(f"📊 Using method: {'Apify (fast)' if agent.use_apify else 'Firecrawl'}")
        print("⏳ Please wait (may take 30-90 seconds)...")
        
        # Check which APIs are available
        has_apify = settings.apify_api_key and settings.apify_api_key != "your-apify-api-key"
        has_firecrawl = settings.firecrawl_api_key and settings.firecrawl_api_key != "fc-YOUR-API-KEY"
        
        if not has_apify and not has_firecrawl:
            print("❌ No API keys configured!")
            print("   Configure at least one:")
            print("   - FIRECRAWL_API_KEY")
            print("   - APIFY_API_KEY")
            return None
        
        # Use available API
        use_apify = has_apify
        if not use_apify and has_firecrawl:
            print("ℹ️  Apify not available, using Firecrawl")
        
        suppliers = await agent.find_suppliers(
            product_name=product,
            min_rating=4.0,
            limit=5,
            use_apify=use_apify
        )
        
        if suppliers:
            print(f"\n✅ Found {len(suppliers)} suppliers!")
            
            # Convert to dict for JSON serialization
            suppliers_data = [s.model_dump() for s in suppliers]
            
            # Save results
            filepath = save_results(
                {
                    "query": product,
                    "method": "apify" if use_apify else "firecrawl",
                    "count": len(suppliers),
                    "suppliers": suppliers_data
                },
                "suppliers_found"
            )
            
            # Display results
            print(f"\n🏪 Top Suppliers:")
            print("="*60)
            for i, s in enumerate(suppliers, 1):
                print(f"{i}. {s.store_name} ({s.marketplace})")
                print(f"   📍 Location: {s.location}")
                print(f"   ⭐ Rating: {s.rating}/5.0")
                print(f"   📦 Product: {s.product_name}")
                print(f"   💰 Price: {s.currency} {s.price:,}")
                if s.phone:
                    print(f"   📞 Phone: {s.phone}")
                if s.email:
                    print(f"   📧 Email: {s.email}")
                print(f"   🔗 URL: {s.product_url}")
                print()
            print("="*60)
            
            return suppliers
        else:
            print("❌ No suppliers found")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"Supplier Scout error: {str(e)}", exc_info=True)
        return None


async def test_multi_marketplace():
    """Test scraping multiple marketplaces"""
    print("\n" + "="*60)
    print("🌐 Test 4: Multi-Marketplace Scraping")
    print("="*60)
    
    if not settings.apify_api_key or settings.apify_api_key == "your-apify-api-key":
        print("❌ Apify API key required for this test")
        print("   Set APIFY_API_KEY in .env file")
        return None
    
    try:
        apify = ApifyIntegration()
        
        product = "skincare"
        print(f"\n🔍 Searching all marketplaces for: {product}")
        print("⏳ Please wait (scraping 3 marketplaces, ~60-120 seconds)...")
        
        results = await apify.scrape_all_marketplaces(
            product_name=product,
            max_items_per_marketplace=5,
            min_rating=4.0
        )
        
        # Count totals
        total = sum(len(v) for v in results.values())
        
        print(f"\n✅ Scraping complete!")
        print(f"   📦 Tokopedia: {len(results['tokopedia'])} products")
        print(f"   📦 Shopee: {len(results['shopee'])} products")
        print(f"   📦 Lazada: {len(results['lazada'])} products")
        print(f"   📦 Total: {total} products")
        
        if total > 0:
            # Save results
            filepath = save_results(
                {
                    "query": product,
                    "marketplaces": {
                        "tokopedia": {"count": len(results['tokopedia']), "products": results['tokopedia']},
                        "shopee": {"count": len(results['shopee']), "products": results['shopee']},
                        "lazada": {"count": len(results['lazada']), "products": results['lazada']}
                    },
                    "total": total
                },
                "multi_marketplace"
            )
            
            # Show sample from each marketplace
            print(f"\n📦 Sample Products from Each Marketplace:")
            print("-" * 60)
            
            for marketplace, items in results.items():
                if items:
                    item = items[0]
                    print(f"\n{marketplace.upper()}:")
                    print(f"  • {item.get('name', 'N/A')}")
                    print(f"  • Price: Rp{item.get('price', 0):,}")
                    print(f"  • Seller: {item.get('sellerName', 'N/A')}")
            
            print("-" * 60)
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"Multi-marketplace error: {str(e)}", exc_info=True)
        return None


async def main():
    """Run all real scraping tests"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║        TrendScout - Real Data Scraping Tests            ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    
    # Check API keys
    print("🔑 Checking API Keys...")
    has_firecrawl = settings.firecrawl_api_key and settings.firecrawl_api_key != "fc-YOUR-API-KEY"
    has_apify = settings.apify_api_key and settings.apify_api_key != "your-apify-api-key"
    has_openai = settings.openai_api_key and settings.openai_api_key != "sk-your-openai-api-key"
    
    print(f"   {'✅' if has_firecrawl else '❌'} Firecrawl API Key")
    print(f"   {'✅' if has_apify else '❌'} Apify API Key")
    print(f"   {'✅' if has_openai else '❌'} OpenAI API Key")
    print()
    
    if not has_firecrawl and not has_apify:
        print("❌ ERROR: No scraping API keys configured!")
        print()
        print("Please configure at least one in .env:")
        print("   FIRECRAWL_API_KEY=fc-your-key")
        print("   APIFY_API_KEY=apify_api_your-key")
        print()
        return
    
    # Create results directory
    Path("./data/scraping_results").mkdir(parents=True, exist_ok=True)
    
    # Run tests based on available APIs
    results = {}
    
    # Test 1: Firecrawl
    if has_firecrawl:
        result = await test_firecrawl_indonetwork()
        results['firecrawl_indonetwork'] = result is not None
    
    # Test 2: Apify Tokopedia
    if has_apify:
        result = await test_apify_tokopedia()
        results['apify_tokopedia'] = result is not None
    
    # Test 3: Full Supplier Scout
    result = await test_supplier_scout_agent()
    results['supplier_scout'] = result is not None
    
    # Test 4: Multi-marketplace (Apify only)
    if has_apify:
        result = await test_multi_marketplace()
        results['multi_marketplace'] = result is not None
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print()
    
    if passed > 0:
        print("✅ Real scraping data has been saved to:")
        print("   ./data/scraping_results/")
        print()
        print("You can view the JSON files to see the scraped data.")
    
    print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        logger.error("Fatal error", exc_info=True)
