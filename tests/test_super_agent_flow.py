#!/usr/bin/env python3
"""
Test Super Agent End-to-End Workflow
Tests the new intent classification and routing system
"""

import asyncio
import logging
import json

from app.agents.super_agent import SuperAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_intent_classification():
    """Test intent classifier with various queries"""
    print("\n" + "="*70)
    print("TEST 1: Intent Classification")
    print("="*70 + "\n")
    
    agent = SuperAgent()
    
    test_queries = [
        "Cari produk skincare yang lagi trending",
        "Supplier tas macrame di Jakarta",
        "Produk home decor trending dan supplier di Bali",
        "Hubungi supplier yang tadi",
        "Gimana status job saya?",
    ]
    
    for query in test_queries:
        print(f"📝 Query: {query}")
        
        intent_result = await agent.intent_classifier.classify(query)
        
        print(f"   Intent: {intent_result['intent']}")
        print(f"   Confidence: {intent_result['confidence']}")
        print(f"   Parameters: {intent_result.get('parameters', {})}")
        print()


async def test_workflow_find_trends():
    """Test finding trending products only"""
    print("\n" + "="*70)
    print("TEST 2: Find Trending Products Workflow")
    print("="*70 + "\n")
    
    agent = SuperAgent()
    
    result = await agent.execute(
        query="Cari produk skincare yang trending",
        user_id="test_user_1"
    )
    
    print(f"✅ Job ID: {result['job_id']}")
    print(f"✅ Status: {result['status']}")
    print(f"✅ Intent: {result.get('intent')}")
    
    if result.get('results'):
        products = result['results'].get('trending_products', [])
        print(f"\n📊 Found {len(products)} trending products:")
        for i, p in enumerate(products[:3], 1):
            print(f"   {i}. {p['name']} (score: {p['trend_score']})")


async def test_workflow_find_suppliers():
    """Test finding suppliers only"""
    print("\n" + "="*70)
    print("TEST 3: Find Suppliers Workflow")
    print("="*70 + "\n")
    
    agent = SuperAgent()
    
    result = await agent.execute(
        query="Cari supplier tas macrame",
        user_id="test_user_2"
    )
    
    print(f"✅ Job ID: {result['job_id']}")
    print(f"✅ Status: {result['status']}")
    print(f"✅ Intent: {result.get('intent')}")
    
    if result.get('results'):
        suppliers = result['results'].get('suppliers', [])
        print(f"\n📦 Found {len(suppliers)} suppliers:")
        for i, s in enumerate(suppliers[:3], 1):
            print(f"   {i}. {s['store_name']} - {s['product_name']}")
            print(f"      Location: {s['location']}")
            print(f"      Price: {s['currency']} {s['price']:,}")


async def test_workflow_full_pipeline():
    """Test full trending + suppliers workflow"""
    print("\n" + "="*70)
    print("TEST 4: Full Pipeline (Trending + Suppliers)")
    print("="*70 + "\n")
    
    agent = SuperAgent()
    
    result = await agent.execute(
        query="Cari produk home decor trending dan supplier di Indonesia",
        user_id="test_user_3"
    )
    
    print(f"✅ Job ID: {result['job_id']}")
    print(f"✅ Status: {result['status']}")
    print(f"✅ Intent: {result.get('intent')}")
    
    if result.get('results'):
        print(f"\n📊 Summary: {result['results'].get('summary', 'N/A')}")
        
        trends = result['results'].get('trending_products', [])
        print(f"\n🔥 Trending Products: {len(trends)}")
        for i, t in enumerate(trends[:2], 1):
            print(f"   {i}. {t['name']}")
        
        suppliers = result['results'].get('suppliers', [])
        print(f"\n📦 Suppliers Found: {len(suppliers)}")
        for i, s in enumerate(suppliers[:3], 1):
            print(f"   {i}. {s['store_name']} - Rp {s['price']:,}")


async def test_all():
    """Run all tests"""
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║        TrendScout Super Agent - E2E Testing              ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    try:
        # Test 1: Intent Classification
        await test_intent_classification()
        
        # Test 2: Find Trends Only
        await test_workflow_find_trends()
        
        # Test 3: Find Suppliers Only
        await test_workflow_find_suppliers()
        
        # Test 4: Full Pipeline
        await test_workflow_full_pipeline()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        logger.error("Test error", exc_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(test_all())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        logger.error("Fatal error", exc_info=True)
