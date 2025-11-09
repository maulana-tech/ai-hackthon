#!/usr/bin/env python3
"""
Quick test script untuk verify scraping fixes
"""
import asyncio
import sys
sys.path.insert(0, '/Users/em/web/ai-hackthon')

from app.integrations.llm_client import LLMClient
from app.agents.bestseller_finder import BestsellerFinder


async def test_llm_apis():
    """Test LLM API connections"""
    print("=" * 60)
    print("🧪 TESTING LLM APIS")
    print("=" * 60)
    
    client = LLMClient()
    
    # Test Gemini
    print("\n1️⃣ Testing Gemini API...")
    try:
        result = await client._generate_gemini(
            prompt="Berikan 1 kata motivasi singkat",
            temperature=0.7,
            max_tokens=50
        )
        if result:
            print(f"   ✅ Gemini working: {result[:100]}")
        else:
            print("   ⚠️ Gemini returned None")
    except Exception as e:
        print(f"   ❌ Gemini error: {str(e)[:200]}")
    
    # Test OpenRouter
    print("\n2️⃣ Testing OpenRouter API...")
    try:
        result = await client._generate_openrouter(
            prompt="Berikan 1 kata motivasi singkat",
            temperature=0.7,
            max_tokens=50
        )
        print(f"   ✅ OpenRouter working: {result[:100]}")
    except Exception as e:
        print(f"   ❌ OpenRouter error: {str(e)[:200]}")
    
    print("\n" + "=" * 60)


async def test_bestseller_scraping():
    """Test bestseller scraping"""
    print("\n" + "=" * 60)
    print("🔍 TESTING BESTSELLER SCRAPING")
    print("=" * 60)
    
    finder = BestsellerFinder()
    
    # Test dengan kategori simple
    print("\n📦 Searching for: 'fashion'")
    try:
        products = await finder.find_bestsellers(
            category="fashion",
            marketplace=None,  # All marketplaces
            limit=5,
            min_sold=50,  # Lower threshold for testing
            min_rating=4.0
        )
        
        if products:
            print(f"\n✅ Found {len(products)} products!")
            for i, p in enumerate(products[:3], 1):
                print(f"\n   {i}. {p.name}")
                print(f"      Platform: {p.platform}")
                print(f"      Rating: {p.rating}/5.0")
                print(f"      Sold: {p.total_sold:,} units" if p.total_sold else "      Sold: N/A")
        else:
            print("\n⚠️ No products found (might be API/credits issue)")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)[:300]}")
    
    print("\n" + "=" * 60)


async def main():
    """Run all tests"""
    print("\n🚀 Starting Scraping Agent Tests\n")
    
    # Test LLM APIs
    await test_llm_apis()
    
    # Wait a bit
    await asyncio.sleep(1)
    
    # Test scraping
    await test_bestseller_scraping()
    
    print("\n✨ Tests completed!\n")


if __name__ == "__main__":
    asyncio.run(main())
