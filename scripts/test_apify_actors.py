"""
Test Apify Actors - Verify marketplace scrapers are working

Tests the newly configured Apify actors:
- jupri/tokopedia-scraper
- best_scraper/shopee-scraper  
- dtrungtin/lazada-scraper
"""
import sys
from pathlib import Path
import asyncio
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.integrations.apify_client import ApifyIntegration
from app.config import get_settings

settings = get_settings()


async def test_actors():
    """Test all Apify actors individually"""
    
    print("=" * 80)
    print("🧪 TESTING APIFY MARKETPLACE ACTORS")
    print("=" * 80)
    print()
    
    # Check API key
    if not settings.apify_api_key or settings.apify_api_key == "your-apify-api-key":
        print("❌ APIFY_API_KEY not configured")
        print()
        print("Please set your Apify API key in .env:")
        print("  APIFY_API_KEY=apify_api_xxxxxxxxxxxxx")
        print()
        print("Get your API key from:")
        print("  https://console.apify.com/account/integrations")
        print()
        return False
    
    print(f"✅ API Key found: {settings.apify_api_key[:15]}...")
    print()
    
    # Initialize Apify client
    apify = ApifyIntegration()
    
    print("=" * 80)
    print("📦 CONFIGURED ACTORS")
    print("=" * 80)
    print()
    print(f"1. Tokopedia: {apify.TOKOPEDIA_ACTOR} ✅ (Primary)")
    print()
    print("Notes:")
    print("  - Shopee: Removed (socket hang up errors)")
    print("  - Lazada: Removed (insufficient credits)")
    print("  - Tokopedia is the most reliable Indonesian marketplace scraper")
    print()
    
    # Test parameters
    test_query = "tas"  # Simple product for testing
    max_items = 5  # Small number for quick test
    
    results = {
        "tokopedia": {"status": "pending", "items": 0, "error": None}
    }
    
    # Test 1: Tokopedia
    print("=" * 80)
    print("TEST 1: TOKOPEDIA SCRAPER")
    print("=" * 80)
    print()
    print(f"Actor: {apify.TOKOPEDIA_ACTOR}")
    print(f"Query: '{test_query}'")
    print(f"Max Items: {max_items}")
    print()
    print("⏳ Running actor... (this may take 30-60 seconds)")
    
    try:
        items = await apify.scrape_tokopedia(
            product_name=test_query,
            max_items=max_items,
            min_rating=4.0
        )
        
        if items:
            results["tokopedia"]["status"] = "success"
            results["tokopedia"]["items"] = len(items)
            print(f"✅ SUCCESS: Found {len(items)} products")
            print()
            
            # Show sample
            if items:
                sample = items[0]
                print("Sample Product:")
                print(f"  Name: {sample.get('name', 'N/A')[:50]}")
                print(f"  Price: {sample.get('price', 'N/A')}")
                print(f"  Shop: {sample.get('shop', 'N/A')}")
                print(f"  Rating: {sample.get('rating', 'N/A')}")
        else:
            results["tokopedia"]["status"] = "warning"
            print("⚠️  No products found")
            print()
            print("💡 Possible reasons:")
            print("   - Insufficient Apify credits (~$0.10 remaining)")
            print("   - Actor needs testing in Apify console first")
            print("   - Rate limiting or region restrictions")
            
    except Exception as e:
        results["tokopedia"]["status"] = "error"
        results["tokopedia"]["error"] = str(e)
        print(f"❌ ERROR: {str(e)}")
        import traceback
        print()
        print("Full traceback:")
        traceback.print_exc()
    
    print()
    
    # Shopee & Lazada removed
    print("=" * 80)
    print("SHOPEE & LAZADA - SKIPPED")
    print("=" * 80)
    print()
    print("⏭️  Shopee: Removed (socket hang up errors)")
    print("   Actor: best_scraper/shopee-scraper has connection issues")
    print()
    print("⏭️  Lazada: Removed (insufficient Apify credits)")
    print("   Need $5+ credits to test properly")
    print()
    print("✅ Tokopedia is sufficient for Indonesian marketplace scraping")
    print()
    
    # Summary
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print()
    
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    warning_count = sum(1 for r in results.values() if r["status"] == "warning")
    error_count = sum(1 for r in results.values() if r["status"] == "error")
    
    for marketplace, result in results.items():
        status_icon = {
            "success": "✅",
            "warning": "⚠️ ",
            "error": "❌",
            "pending": "⏳"
        }.get(result["status"], "❓")
        
        print(f"{status_icon} {marketplace.upper()}")
        print(f"   Status: {result['status']}")
        print(f"   Items: {result['items']}")
        if result["error"]:
            print(f"   Error: {result['error'][:60]}...")
        print()
    
    print("-" * 80)
    print(f"Results: {success_count} success, {warning_count} warnings, {error_count} errors")
    print()
    
    if success_count > 0:
        print("=" * 80)
        print("✅ ACTORS ARE WORKING!")
        print("=" * 80)
        print()
        print(f"At least {success_count} actor(s) successfully scraped data.")
        print()
        print("Your Apify configuration is correct!")
        print()
        return True
    elif warning_count > 0:
        print("=" * 80)
        print("⚠️  ACTORS CONFIGURED BUT NO DATA")
        print("=" * 80)
        print()
        print("Actors ran without errors but returned no data.")
        print("This could be:")
        print("  - Rate limiting")
        print("  - Empty search results")
        print("  - Actor needs different input format")
        print()
        print("Try testing with different queries or check Apify console:")
        print("  https://console.apify.com/")
        print()
        return False
    else:
        print("=" * 80)
        print("❌ ALL ACTORS FAILED")
        print("=" * 80)
        print()
        print("Please check:")
        print("  1. API key is correct")
        print("  2. You have Apify credits")
        print("  3. Actor names are correct")
        print("  4. Actors are accessible in your account")
        print()
        print("View errors above for details.")
        print()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_actors())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
