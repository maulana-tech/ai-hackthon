"""
Test Bestseller Finder - Advanced product discovery from marketplaces
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.bestseller_finder import BestsellerFinder
from app.agents.super_agent import SuperAgent
from app.config import get_settings

async def test_direct_bestseller_scraping():
    """Test BestsellerFinder directly"""
    
    print("=" * 80)
    print("TEST 1: DIRECT BESTSELLER FINDER")
    print("=" * 80)
    print()
    
    finder = BestsellerFinder()
    
    # Test 1: Find bestsellers without category (general)
    print("🔍 Test 1.1: Finding general bestsellers...")
    print()
    
    bestsellers = await finder.find_bestsellers(
        category=None,
        marketplace=None,
        limit=5,
        min_sold=50,  # Lower threshold for testing
        min_rating=4.0
    )
    
    if bestsellers:
        print(f"✅ Found {len(bestsellers)} bestselling products!\n")
        
        for i, product in enumerate(bestsellers, 1):
            print(f"{i}. {product.name}")
            print(f"   📊 Trend Score: {product.trend_score:.1f}/100")
            print(f"   ⭐ Rating: {product.rating:.1f}/5.0 ({product.review_count:,} reviews)")
            print(f"   🛒 Total Sold: {(product.total_sold or 0):,} units")
            print(f"   💰 Price: {product.price_range}")
            print(f"   🏪 Platform: {product.platform}")
            print(f"   📍 Seller: {product.shop_name} ({product.shop_location})")
            print(f"   {'✅ Official Store' if product.is_official else ''}")
            print()
    else:
        print("❌ No bestsellers found")
    
    # Test 2: Find fashion bestsellers
    print("\n" + "=" * 80)
    print("🔍 Test 1.2: Finding fashion bestsellers...")
    print("=" * 80)
    print()
    
    fashion_bestsellers = await finder.find_bestsellers(
        category="fashion",
        marketplace=None,
        limit=3,
        min_sold=50,
        min_rating=4.0
    )
    
    if fashion_bestsellers:
        print(f"✅ Found {len(fashion_bestsellers)} fashion bestsellers!\n")
        
        # Generate report
        report = await finder.generate_bestseller_report(fashion_bestsellers)
        print(report)
    else:
        print("❌ No fashion bestsellers found")

async def test_super_agent_integration():
    """Test SuperAgent with natural language queries"""
    
    print("\n" + "=" * 80)
    print("TEST 2: SUPER AGENT NATURAL LANGUAGE QUERIES")
    print("=" * 80)
    print()
    
    agent = SuperAgent()
    
    test_queries = [
        "Carikan produk yang paling laris",
        "Produk apa yang paling banyak terjual?",
        "Cari produk fashion yang bestseller",
        "Tampilkan produk terlaris di Tokopedia",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"Query {i}: {query}")
        print(f"{'='*80}\n")
        
        try:
            result = await agent.execute(
                query=query,
                user_id="test_user_123"
            )
            
            print(f"Intent: {result.get('intent', 'unknown')}")
            print(f"Status: {result.get('status', 'unknown')}")
            print()
            
            if result.get('status') == 'completed':
                results_data = result.get('results', {})
                
                if 'bestsellers' in results_data:
                    bestsellers = results_data['bestsellers']
                    print(f"✅ Found {len(bestsellers)} bestsellers")
                    
                    # Show top 3
                    for j, product in enumerate(bestsellers[:3], 1):
                        print(f"\n{j}. {product['name']}")
                        print(f"   Score: {product.get('trend_score', 0):.1f}/100")
                        print(f"   Sold: {product.get('total_sold', 0):,} units")
                        print(f"   Platform: {product.get('platform', 'Unknown')}")
                    
                    # Show summary
                    if 'summary' in results_data:
                        summary = results_data['summary']
                        print(f"\n📊 Summary:")
                        print(f"   Total Sold: {summary.get('total_sold', 0):,} units")
                        print(f"   Avg Rating: {summary.get('avg_rating', 0):.2f}/5.0")
                        print(f"   Official Stores: {summary.get('official_stores', 0)}")
                        print(f"   Platforms: {', '.join(summary.get('marketplaces', []))}")
                
                # Show report if available
                if 'report' in results_data:
                    print("\n" + "="*80)
                    print("DETAILED REPORT:")
                    print("="*80)
                    print(results_data['report'][:500] + "..." if len(results_data['report']) > 500 else results_data['report'])
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

async def test_intent_classification():
    """Test that IntentClassifier correctly identifies bestseller queries"""
    
    print("\n" + "=" * 80)
    print("TEST 3: INTENT CLASSIFICATION")
    print("=" * 80)
    print()
    
    from app.agents.intent_classifier import IntentClassifier
    
    classifier = IntentClassifier()
    
    test_queries = [
        "Carikan produk yang paling laris",
        "Produk apa yang bestseller?",
        "Tampilkan produk terlaris",
        "Cari produk fashion yang paling banyak terjual",
        "Produk paling laris di Shopee",
    ]
    
    for query in test_queries:
        print(f"Query: \"{query}\"")
        
        result = await classifier.classify(query)
        
        print(f"  → Intent: {result['intent']}")
        print(f"  → Confidence: {result['confidence']:.2f}")
        print(f"  → Parameters: {result.get('parameters', {})}")
        print()

async def main():
    """Run all tests"""
    
    settings = get_settings()
    
    # Check API keys
    if not settings.firecrawl_api_key or settings.firecrawl_api_key == "fc-YOUR-API-KEY":
        print("⚠️  WARNING: Firecrawl API key not configured")
        print("   Some tests may fail without proper API configuration")
        print()
    
    # Run tests
    print("\n🚀 Starting Bestseller Finder Tests\n")
    
    # Test 1: Direct scraping
    await test_direct_bestseller_scraping()
    
    # Test 2: Super Agent integration
    await test_super_agent_integration()
    
    # Test 3: Intent classification
    await test_intent_classification()
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
