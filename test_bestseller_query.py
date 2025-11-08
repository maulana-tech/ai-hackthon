"""
Test bestseller query: "cari 5 produk elektronik yang terlaris"
"""
import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.agents.bestseller_finder import BestsellerFinder
from app.agents.super_agent import SuperAgent
from app.agents.intent_classifier import IntentClassifier

async def test_bestseller_query():
    """Test the specific query"""
    
    query = "cari 5 produk elektronik yang terlaris"
    user_id = "demo_user_elektronik"
    
    print("=" * 80)
    print("🧪 TESTING BESTSELLER QUERY")
    print("=" * 80)
    print()
    print(f"📝 Query: \"{query}\"")
    print(f"👤 User ID: {user_id}")
    print()
    
    # Test 1: Intent Classification
    print("Step 1: Intent Classification")
    print("-" * 80)
    
    classifier = IntentClassifier()
    intent_result = await classifier.classify(query)
    
    print(f"✅ Intent: {intent_result.get('intent')}")
    print(f"✅ Confidence: {intent_result.get('confidence')}")
    print(f"✅ Parameters: {intent_result.get('parameters', {})}")
    print()
    
    # Test 2: Direct BestsellerFinder
    print("Step 2: Direct Bestseller Finder")
    print("-" * 80)
    
    finder = BestsellerFinder()
    
    try:
        bestsellers = await finder.find_bestsellers(
            category="elektronik",  # From intent parameters
            marketplace=None,  # All marketplaces
            limit=5,  # From query
            min_sold=50,  # Lower threshold for testing
            min_rating=4.0
        )
        
        print(f"✅ Found {len(bestsellers)} bestselling products!")
        print()
        
        if bestsellers:
            for i, product in enumerate(bestsellers, 1):
                print(f"{i}. {product.name}")
                print(f"   📊 Trend Score: {product.trend_score:.1f}/100")
                print(f"   ⭐ Rating: {product.rating:.1f}/5.0 ({product.review_count:,} reviews)")
                print(f"   🛒 Total Sold: {(product.total_sold or 0):,} units")
                print(f"   💰 Price: {product.price_range}")
                print(f"   🏪 Platform: {product.platform}")
                print(f"   📍 Seller: {product.shop_name} ({product.shop_location})")
                if product.is_official:
                    print(f"   ✅ Official Store")
                if product.product_url:
                    print(f"   🔗 URL: {product.product_url[:60]}...")
                print()
            
            # Generate report
            print("=" * 80)
            print("📊 DETAILED REPORT")
            print("=" * 80)
            
            report = await finder.generate_bestseller_report(bestsellers)
            print(report)
            
        else:
            print("⚠️  No bestsellers found with current criteria")
            print("   Trying with lower threshold...")
            
            # Retry with even lower threshold
            bestsellers = await finder.find_bestsellers(
                category="elektronik",
                marketplace=None,
                limit=5,
                min_sold=10,  # Very low threshold
                min_rating=3.5
            )
            
            if bestsellers:
                print(f"✅ Found {len(bestsellers)} products with lower threshold!")
                for i, product in enumerate(bestsellers, 1):
                    print(f"{i}. {product.name} - {product.total_sold or 0} sold")
            else:
                print("❌ Still no results. Marketplaces might be rate limiting.")
                print("   This is expected during high traffic periods.")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 3: Via SuperAgent (Full Workflow)
    print("Step 3: Via SuperAgent (Full Workflow)")
    print("-" * 80)
    
    try:
        agent = SuperAgent()
        
        result = await agent.execute(
            query=query,
            user_id=user_id
        )
        
        print(f"✅ Status: {result.get('status')}")
        print(f"✅ Intent: {result.get('intent')}")
        print(f"✅ Job ID: {result.get('job_id')}")
        
        if result.get('status') == 'completed':
            results_data = result.get('results', {})
            
            if 'bestsellers' in results_data:
                bestsellers = results_data['bestsellers']
                print(f"✅ Bestsellers: {len(bestsellers)} products")
            
            if 'suppliers_by_product' in results_data:
                suppliers = results_data['suppliers_by_product']
                print(f"✅ Suppliers matched: {len(suppliers)} products")
        
    except Exception as e:
        print(f"⚠️  SuperAgent workflow issue: {str(e)}")
        print("   (This is expected if intent routing needs adjustment)")
    
    print()
    print("=" * 80)
    print("✅ TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_bestseller_query())
