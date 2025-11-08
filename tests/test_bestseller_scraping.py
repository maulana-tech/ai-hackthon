"""
Test script for bestseller scraping with contact information
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.supplier_scout import SupplierScoutAgent
from app.config import get_settings

async def test_bestseller_scraping():
    """Test scraping bestselling products with contact info"""
    
    print("=" * 70)
    print("BESTSELLER SUPPLIER SCRAPING TEST")
    print("=" * 70)
    print()
    
    # Initialize agent
    scout = SupplierScoutAgent()
    
    # Test products
    test_queries = [
        {
            "product": "skincare",
            "location": None,
            "min_rating": 4.0,
            "limit": 3
        },
        {
            "product": "tas selempang",
            "location": "Jakarta",
            "min_rating": 4.5,
            "limit": 3
        },
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {query['product'].upper()}")
        print(f"{'='*70}\n")
        
        try:
            # Search for suppliers
            print(f"🔍 Searching for bestselling '{query['product']}' suppliers...")
            print(f"   Location: {query['location'] or 'All Indonesia'}")
            print(f"   Min Rating: {query['min_rating']}")
            print(f"   Limit: {query['limit']}")
            print()
            
            suppliers = await scout.find_suppliers(
                product_name=query['product'],
                location=query['location'],
                min_rating=query['min_rating'],
                limit=query['limit'],
                use_apify=False  # Use Firecrawl for testing
            )
            
            if not suppliers:
                print("❌ No suppliers found")
                continue
            
            print(f"✅ Found {len(suppliers)} suppliers\n")
            
            # Display results
            for j, supplier in enumerate(suppliers, 1):
                print(f"{j}. {'🔥' if supplier.is_bestseller else '  '} {supplier.store_name} ({supplier.marketplace})")
                print(f"   Product: {supplier.product_name}")
                print(f"   Rating: {supplier.rating}/5.0", end="")
                if supplier.review_count:
                    print(f" ({supplier.review_count} reviews)", end="")
                print()
                
                if supplier.total_sold:
                    print(f"   Total Sold: {supplier.total_sold:,} pcs")
                
                if supplier.phone:
                    print(f"   📞 Phone: {supplier.phone}")
                if supplier.whatsapp and supplier.whatsapp != supplier.phone:
                    print(f"   💬 WhatsApp: {supplier.whatsapp}")
                if supplier.email:
                    print(f"   📧 Email: {supplier.email}")
                
                print(f"   Location: {supplier.city}")
                print(f"   Price: Rp {supplier.price:,.0f}")
                print(f"   Min Order: {supplier.minimum_order} pcs")
                print(f"   Stock: {'✅ Available' if supplier.stock_available else '❌ Out'}")
                if supplier.verified:
                    print(f"   ✅ Verified")
                print()
            
            # Generate and show summary
            print("\n" + "─" * 70)
            print("SUMMARY")
            print("─" * 70 + "\n")
            
            summary = await scout.generate_search_summary(suppliers)
            print(summary)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETED")
    print("=" * 70)

async def test_contact_extraction():
    """Test contact information extraction specifically"""
    
    print("\n" + "=" * 70)
    print("CONTACT INFORMATION EXTRACTION TEST")
    print("=" * 70)
    print()
    
    scout = SupplierScoutAgent()
    
    # Test with Indonetwork (B2B - should have contact info)
    print("Testing Indonetwork B2B supplier scraping...")
    print()
    
    try:
        suppliers = await scout._search_indonetwork("furniture", min_rating=4.0)
        
        if suppliers:
            print(f"✅ Found {len(suppliers)} Indonetwork suppliers\n")
            
            contact_count = sum(1 for s in suppliers if s.phone or s.email)
            print(f"📊 Suppliers with contact info: {contact_count}/{len(suppliers)}\n")
            
            for i, supplier in enumerate(suppliers[:3], 1):
                print(f"{i}. {supplier.store_name}")
                if supplier.phone:
                    print(f"   📞 Phone: {supplier.phone}")
                if supplier.whatsapp:
                    print(f"   💬 WhatsApp: {supplier.whatsapp}")
                if supplier.email:
                    print(f"   📧 Email: {supplier.email}")
                print(f"   📍 Location: {supplier.location}")
                print()
        else:
            print("❌ No Indonetwork suppliers found")
            
    except Exception as e:
        print(f"❌ Error testing Indonetwork: {str(e)}")

async def main():
    """Run all tests"""
    
    settings = get_settings()
    
    # Check if API keys are configured
    if not settings.firecrawl_api_key or settings.firecrawl_api_key == "fc-YOUR-API-KEY":
        print("⚠️  WARNING: Firecrawl API key not configured in .env")
        print("   Set FIRECRAWL_API_KEY in your .env file")
        return
    
    print(f"\n🔥 Firecrawl API Key: {settings.firecrawl_api_key[:10]}...")
    
    # Run tests
    await test_bestseller_scraping()
    await test_contact_extraction()

if __name__ == "__main__":
    asyncio.run(main())
