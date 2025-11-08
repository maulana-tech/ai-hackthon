#!/usr/bin/env python3
"""
Test script untuk TrendScout Supplier Connector
Jalankan: uv run python test_agent.py
"""

import asyncio
import json
from app.agents.super_agent import SuperAgent

async def test_full_workflow():
    """Test complete workflow"""
    
    print("="*60)
    print("🚀 TrendScout Supplier Connector - Test")
    print("="*60)
    
    super_agent = SuperAgent()
    
    query = "LED face mask"
    user_id = "test_user_001"
    
    print(f"\n📝 Query: {query}")
    print(f"👤 User ID: {user_id}")
    print("\n⏳ Executing workflow...\n")
    
    try:
        report = await super_agent.execute_full_workflow(
            query=query,
            user_id=user_id,
            quantity=20,
            region="global",
            location="Jakarta",
            auto_contact=False  # Set False untuk testing tanpa kirim pesan
        )
        
        print("\n" + "="*60)
        print("✅ WORKFLOW COMPLETED!")
        print("="*60)
        
        print(f"\n📊 Job ID: {report.job_id}")
        print(f"\n🔍 Trending Products Found: {len(report.trending_products)}")
        
        for i, product in enumerate(report.trending_products, 1):
            print(f"\n  {i}. {product.name}")
            print(f"     Category: {product.category}")
            print(f"     Trend Score: {product.trend_score:.1f}/100")
            print(f"     Growth: +{product.growth_percentage:.1f}%")
            print(f"     Platform: {product.platform}")
            print(f"     Search Volume: {product.search_volume:,}")
        
        print(f"\n🏪 Suppliers Found: {len(report.suppliers)}")
        
        for i, supplier in enumerate(report.suppliers, 1):
            print(f"\n  {i}. {supplier.store_name}")
            print(f"     Marketplace: {supplier.marketplace}")
            print(f"     Location: {supplier.city}")
            print(f"     Rating: {supplier.rating}/5.0")
            print(f"     Price: Rp {supplier.price:,.0f}")
            print(f"     Min Order: {supplier.minimum_order} pcs")
            print(f"     Stock: {'✓ Available' if supplier.stock_available else '✗ Out'}")
        
        print(f"\n📧 Outreach Messages: {len(report.outreach_results)}")
        
        if report.outreach_results:
            for msg in report.outreach_results:
                status_icon = "✅" if msg.status == "sent" else "❌"
                print(f"  {status_icon} {msg.channel.upper()}: {msg.supplier_name}")
        
        print("\n" + "="*60)
        print("📈 SUMMARY")
        print("="*60)
        print(report.summary)
        
        print("\n" + "="*60)
        print("💡 RECOMMENDATIONS")
        print("="*60)
        for i, rec in enumerate(report.recommendations, 1):
            print(f"{i}. {rec}")
        
        print("\n" + "="*60)
        print("📋 NEXT STEPS")
        print("="*60)
        for i, step in enumerate(report.next_steps, 1):
            print(f"{i}. {step}")
        
        print("\n" + "="*60)
        print("✅ Test completed successfully!")
        print("="*60)
        
        with open("data/test_report.json", "w") as f:
            json.dump(report.model_dump(), f, indent=2, default=str)
        print("\n💾 Full report saved to: data/test_report.json")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_trend_analysis_only():
    """Test trend analysis only"""
    
    print("\n" + "="*60)
    print("🔍 Testing Trend Analysis Only")
    print("="*60)
    
    super_agent = SuperAgent()
    
    products = await super_agent.trend_analyst.analyze_trends(
        query="skincare products",
        region="global",
        limit=3
    )
    
    print(f"\nFound {len(products)} trending products:")
    
    for i, product in enumerate(products, 1):
        print(f"\n{i}. {product.name}")
        print(f"   Trend Score: {product.trend_score:.1f}")
        print(f"   Platform: {product.platform}")

async def test_supplier_search_only():
    """Test supplier search only"""
    
    print("\n" + "="*60)
    print("🏪 Testing Supplier Search Only")
    print("="*60)
    
    super_agent = SuperAgent()
    
    suppliers = await super_agent.supplier_scout.find_suppliers(
        product_name="LED face mask",
        location="Jakarta",
        min_rating=4.0,
        limit=5
    )
    
    print(f"\nFound {len(suppliers)} suppliers:")
    
    for i, supplier in enumerate(suppliers, 1):
        print(f"\n{i}. {supplier.store_name}")
        print(f"   Location: {supplier.city}")
        print(f"   Rating: {supplier.rating}/5.0")
        print(f"   Price: Rp {supplier.price:,.0f}")

if __name__ == "__main__":
    print("\n🤖 TrendScout Supplier Connector - Test Suite\n")
    print("Select test:")
    print("1. Full Workflow (Recommended)")
    print("2. Trend Analysis Only")
    print("3. Supplier Search Only")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(test_full_workflow())
    elif choice == "2":
        asyncio.run(test_trend_analysis_only())
    elif choice == "3":
        asyncio.run(test_supplier_search_only())
    else:
        print("Invalid choice!")
