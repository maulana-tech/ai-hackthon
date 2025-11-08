#!/usr/bin/env python3
"""
Real Supplier Scraping - Extract actual supplier data

This script scrapes real supplier information from:
1. Indonetwork (B2B)
2. Tokopedia (if Firecrawl works)
3. Uses Apify if API key available

Saves results to CSV and JSON for easy viewing.
"""

import asyncio
import logging
import json
import csv
from datetime import datetime
from pathlib import Path

from app.config import get_settings
from app.agents.supplier_scout import SupplierScoutAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
settings = get_settings()


def save_to_json(data: dict, filename: str):
    """Save to JSON file"""
    output_dir = Path("./data/suppliers")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = output_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    return filepath


def save_to_csv(suppliers: list, filename: str):
    """Save suppliers to CSV file"""
    output_dir = Path("./data/suppliers")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = output_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    if not suppliers:
        return None
    
    # CSV headers
    headers = [
        'Store Name', 'Marketplace', 'Location', 'Rating', 
        'Product Name', 'Price', 'Currency', 'MOQ', 
        'Stock Available', 'Phone', 'Email', 'Product URL'
    ]
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for s in suppliers:
            writer.writerow({
                'Store Name': s.get('store_name', ''),
                'Marketplace': s.get('marketplace', ''),
                'Location': s.get('location', ''),
                'Rating': s.get('rating', ''),
                'Product Name': s.get('product_name', ''),
                'Price': s.get('price', ''),
                'Currency': s.get('currency', ''),
                'MOQ': s.get('moq', ''),
                'Stock Available': s.get('stock_available', ''),
                'Phone': s.get('phone', ''),
                'Email': s.get('email', ''),
                'Product URL': s.get('product_url', '')
            })
    
    return filepath


async def scrape_product(product_name: str, min_rating: float = 4.0, limit: int = 10):
    """Scrape suppliers for a product"""
    print(f"\n{'='*60}")
    print(f"🔍 Scraping Suppliers: {product_name}")
    print(f"{'='*60}")
    print(f"⚙️  Settings:")
    print(f"   • Min Rating: {min_rating}/5.0")
    print(f"   • Max Results: {limit}")
    print(f"   • Using: Firecrawl")
    print()
    
    try:
        agent = SupplierScoutAgent()
        
        print("⏳ Scraping... (this may take 30-90 seconds)")
        print()
        
        suppliers = await agent.find_suppliers(
            product_name=product_name,
            min_rating=min_rating,
            limit=limit,
            use_apify=False  # Force Firecrawl for B2B data
        )
        
        if suppliers:
            print(f"✅ Found {len(suppliers)} suppliers!")
            print()
            
            # Convert to dict
            suppliers_data = [s.model_dump() for s in suppliers]
            
            # Save to JSON
            json_file = save_to_json(
                {
                    "product": product_name,
                    "scraped_at": datetime.now().isoformat(),
                    "count": len(suppliers),
                    "suppliers": suppliers_data
                },
                f"suppliers_{product_name.replace(' ', '_')}"
            )
            print(f"💾 Saved to JSON: {json_file}")
            
            # Save to CSV
            csv_file = save_to_csv(
                suppliers_data,
                f"suppliers_{product_name.replace(' ', '_')}"
            )
            if csv_file:
                print(f"💾 Saved to CSV: {csv_file}")
            
            print()
            print(f"📊 Supplier Summary:")
            print(f"{'='*60}")
            
            for i, s in enumerate(suppliers, 1):
                print(f"\n{i}. {s.store_name}")
                print(f"   🏢 Marketplace: {s.marketplace}")
                print(f"   📍 Location: {s.location}")
                print(f"   ⭐ Rating: {s.rating}/5.0")
                print(f"   📦 Product: {s.product_name}")
                print(f"   💰 Price: {s.currency} {s.price:,}")
                print(f"   📊 MOQ: {s.minimum_order} units")
                if s.phone:
                    print(f"   📞 Phone: {s.phone}")
                if s.email:
                    print(f"   📧 Email: {s.email}")
                print(f"   🔗 URL: {s.product_url}")
            
            print(f"\n{'='*60}")
            
            return suppliers
        else:
            print("❌ No suppliers found")
            print("💡 Try:")
            print("   • Different product name")
            print("   • Lower min_rating")
            print("   • Check API keys in .env")
            return []
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"Scraping error: {str(e)}", exc_info=True)
        return []


async def main():
    """Main scraping function"""
    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║      TrendScout - Real Supplier Data Scraping           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    
    # Check API keys
    has_firecrawl = settings.firecrawl_api_key and settings.firecrawl_api_key != "fc-YOUR-API-KEY"
    
    if not has_firecrawl:
        print("❌ FIRECRAWL_API_KEY not configured!")
        print("   Please set it in .env file")
        print()
        return
    
    print("✅ Firecrawl API Key configured")
    print()
    
    # Products to scrape
    products = [
        ("macrame wall hanging", 4.0, 5),
        ("tas macrame", 4.0, 5),
        # ("skincare serum", 4.5, 10),
        # ("LED lamp", 4.0, 8),
    ]
    
    print(f"📋 Will scrape {len(products)} products:")
    for i, (product, rating, limit) in enumerate(products, 1):
        print(f"   {i}. {product} (min rating: {rating}, limit: {limit})")
    print()
    
    # Scrape each product
    all_results = []
    
    for product, min_rating, limit in products:
        suppliers = await scrape_product(product, min_rating, limit)
        all_results.append({
            "product": product,
            "count": len(suppliers),
            "suppliers": [s.model_dump() if hasattr(s, 'model_dump') else s for s in suppliers]
        })
        
        # Wait between scrapes
        if product != products[-1][0]:
            print("\n⏳ Waiting 3 seconds before next scrape...")
            await asyncio.sleep(3)
    
    # Final summary
    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                  Scraping Complete!                      ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    
    total_suppliers = sum(r['count'] for r in all_results)
    
    print(f"📊 Summary:")
    print(f"   • Products scraped: {len(products)}")
    print(f"   • Total suppliers found: {total_suppliers}")
    print()
    
    for result in all_results:
        print(f"   • {result['product']}: {result['count']} suppliers")
    
    print()
    print(f"💾 All results saved to: ./data/suppliers/")
    print()
    print("✅ You can now view the CSV or JSON files!")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        logger.error("Fatal error", exc_info=True)
