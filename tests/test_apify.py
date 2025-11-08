#!/usr/bin/env python3
"""
Test script for Apify integration
"""

import asyncio
import logging
from app.integrations.apify_client import ApifyIntegration
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
settings = get_settings()


async def test_apify_connection():
    """Test Apify API connection"""
    print("=" * 60)
    print("Testing Apify Integration")
    print("=" * 60)
    print()
    
    apify = ApifyIntegration()
    
    # Test 1: Get usage stats
    print("1️⃣ Testing Apify connection & usage stats...")
    try:
        stats = await apify.get_usage_stats()
        if stats.get("success"):
            print(f"✅ Connected to Apify!")
            usage = stats.get("usage", {})
            print(f"   Credits used: ${usage.get('credits_used', 0)}")
            print(f"   Credits limit: ${usage.get('credits_limit', 0)}")
        else:
            print(f"❌ Failed: {stats.get('error')}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()


async def test_tokopedia_scrape():
    """Test Tokopedia scraping"""
    print("2️⃣ Testing Tokopedia scraping...")
    
    apify = ApifyIntegration()
    
    try:
        products = await apify.scrape_tokopedia(
            product_name="macrame",
            max_items=5,
            min_rating=4.0
        )
        
        if products:
            print(f"✅ Found {len(products)} products on Tokopedia")
            for i, p in enumerate(products[:3], 1):
                print(f"   {i}. {p.get('name', 'N/A')}")
                print(f"      Price: Rp{p.get('price', 0):,}")
                print(f"      Seller: {p.get('sellerName', 'N/A')}")
                print(f"      Rating: {p.get('sellerRating', 0)}/5.0")
        else:
            print("⚠️  No products found")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()


async def test_all_marketplaces():
    """Test all marketplaces scraping"""
    print("3️⃣ Testing multi-marketplace scraping...")
    
    apify = ApifyIntegration()
    
    try:
        results = await apify.scrape_all_marketplaces(
            product_name="skincare",
            max_items_per_marketplace=5,
            min_rating=4.0
        )
        
        print(f"✅ Marketplace scraping completed!")
        print(f"   Tokopedia: {len(results['tokopedia'])} products")
        print(f"   Shopee: {len(results['shopee'])} products")
        print(f"   Lazada: {len(results['lazada'])} products")
        print(f"   Total: {sum(len(v) for v in results.values())} products")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()


async def test_supplier_conversion():
    """Test conversion to Supplier objects"""
    print("4️⃣ Testing Supplier object conversion...")
    
    apify = ApifyIntegration()
    
    try:
        suppliers = await apify.get_suppliers_from_all_marketplaces(
            product_name="macrame",
            max_suppliers=10,
            min_rating=4.0
        )
        
        if suppliers:
            print(f"✅ Found {len(suppliers)} suppliers")
            for i, s in enumerate(suppliers[:5], 1):
                print(f"   {i}. {s.store_name} ({s.marketplace})")
                print(f"      Location: {s.location}")
                print(f"      Rating: {s.rating}/5.0")
                print(f"      Product: {s.product_name}")
                print(f"      Price: {s.currency} {s.price:,}")
        else:
            print("⚠️  No suppliers found")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()


async def main():
    """Run all tests"""
    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║          Apify Integration Test Suite                    ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    
    # Check API key
    if not settings.apify_api_key or settings.apify_api_key == "your-apify-api-key":
        print("❌ APIFY_API_KEY not configured in .env")
        print()
        print("Please:")
        print("1. Get API key from https://console.apify.com")
        print("2. Add to .env: APIFY_API_KEY=apify_api_xxxxx")
        print()
        return
    
    print(f"✅ API Key configured: {settings.apify_api_key[:20]}...")
    print()
    
    # Run tests
    await test_apify_connection()
    
    # Ask to continue (these tests use credits)
    print("⚠️  The following tests will use Apify credits (small amount)")
    response = input("Continue with scraping tests? (y/n): ")
    
    if response.lower() == 'y':
        await test_tokopedia_scrape()
        await test_all_marketplaces()
        await test_supplier_conversion()
        
        print("=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
    else:
        print("Tests cancelled.")


if __name__ == "__main__":
    asyncio.run(main())
