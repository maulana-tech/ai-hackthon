#!/usr/bin/env python3
"""
Test scraping untuk Tokopedia, Shopee, dan Lazada dengan Apify key baru
"""
import asyncio
import sys
sys.path.insert(0, '/Users/em/web/ai-hackthon')

from app.integrations.apify_client import ApifyIntegration
from app.config import get_settings

settings = get_settings()

async def test_marketplace_scraping():
    """Test scraping dari ketiga marketplace"""
    
    print("=" * 70)
    print("🧪 TESTING MARKETPLACE SCRAPING WITH NEW APIFY KEY")
    print("=" * 70)
    print(f"\n🔑 Apify Key: {settings.apify_api_key[:20]}...")
    print()
    
    apify = ApifyIntegration()
    
    # Test query
    search_query = "sepatu sneakers"
    max_items = 10
    min_rating = 4.0
    
    print(f"📦 Search Query: '{search_query}'")
    print(f"📊 Max Items: {max_items}")
    print(f"⭐ Min Rating: {min_rating}")
    print()
    
    # Test 1: Tokopedia
    print("─" * 70)
    print("1️⃣  TESTING TOKOPEDIA SCRAPING")
    print("─" * 70)
    try:
        print(f"🔍 Scraping Tokopedia for '{search_query}'...")
        tokopedia_results = await apify.scrape_tokopedia(
            product_name=search_query,
            max_items=max_items,
            min_rating=min_rating
        )
        
        if tokopedia_results:
            print(f"✅ SUCCESS: Found {len(tokopedia_results)} products from Tokopedia")
            for i, item in enumerate(tokopedia_results[:3], 1):
                name = item.get('name', 'N/A')
                price = item.get('price', 'N/A')
                rating = item.get('rating', 'N/A')
                print(f"   {i}. {name[:60]}")
                print(f"      Price: {price}, Rating: {rating}")
        else:
            print("⚠️  No results from Tokopedia (check credits or query)")
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:200]}")
    
    print()
    
    # Test 2: Lazada
    print("─" * 70)
    print("2️⃣  TESTING LAZADA SCRAPING")
    print("─" * 70)
    try:
        print(f"🔍 Scraping Lazada for '{search_query}'...")
        lazada_results = await apify.scrape_lazada(
            product_name=search_query,
            max_items=max_items,
            min_rating=min_rating
        )
        
        if lazada_results:
            print(f"✅ SUCCESS: Found {len(lazada_results)} products from Lazada")
            for i, item in enumerate(lazada_results[:3], 1):
                name = item.get('name', 'N/A')
                price = item.get('price', 'N/A')
                rating = item.get('rating', 'N/A')
                print(f"   {i}. {name[:60]}")
                print(f"      Price: {price}, Rating: {rating}")
        else:
            print("⚠️  No results from Lazada (check credits or query)")
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:200]}")
    
    print()
    
    # Test 3: Shopee
    print("─" * 70)
    print("3️⃣  TESTING SHOPEE SCRAPING")
    print("─" * 70)
    try:
        print(f"🔍 Scraping Shopee for '{search_query}'...")
        shopee_results = await apify.scrape_shopee(
            product_name=search_query,
            max_items=max_items,
            min_rating=min_rating
        )
        
        if shopee_results:
            print(f"✅ SUCCESS: Found {len(shopee_results)} products from Shopee")
            for i, item in enumerate(shopee_results[:3], 1):
                name = item.get('name', item.get('title', 'N/A'))
                price = item.get('price', 'N/A')
                rating = item.get('rating', item.get('shop_rating', 'N/A'))
                print(f"   {i}. {name[:60]}")
                print(f"      Price: {price}, Rating: {rating}")
        else:
            print("⚠️  No results from Shopee (check credits or query)")
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:200]}")
    
    print()
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    # Summary table
    results = {
        "Tokopedia": len(tokopedia_results) if 'tokopedia_results' in locals() else 0,
        "Lazada": len(lazada_results) if 'lazada_results' in locals() else 0,
        "Shopee": len(shopee_results) if 'shopee_results' in locals() else 0
    }
    
    for marketplace, count in results.items():
        status = "✅" if count > 0 else "❌"
        print(f"{status} {marketplace:15s}: {count} products")
    
    total = sum(results.values())
    print(f"\n🎯 Total Products: {total}")
    
    if total > 0:
        print("\n✅ NEW APIFY KEY WORKING!")
    else:
        print("\n⚠️  Check Apify credits or actor configurations")
    
    print()


if __name__ == "__main__":
    asyncio.run(test_marketplace_scraping())
