#!/usr/bin/env python3
"""
Bulk Data Scraping - Scrape banyak produk sekaligus untuk training data
"""

import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path

from app.agents.supplier_scout import SupplierScoutAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def scrape_bulk_products():
    """Scrape multiple product categories"""
    
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║      TrendScout - Bulk Data Scraping                    ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")
    
    # Daftar produk untuk di-scrape
    products = [
        # Fashion & Accessories
        ("tas macrame", 3.5, 10),
        ("dompet wanita", 3.5, 10),
        ("sepatu sneakers", 3.5, 10),
        ("kaos polos", 3.5, 10),
        
        # Home & Living
        ("lampu hias", 3.5, 10),
        ("vas bunga", 3.5, 10),
        ("gorden minimalis", 3.5, 10),
        
        # Electronics
        ("power bank", 4.0, 10),
        ("kabel charger", 3.5, 10),
        ("headset bluetooth", 4.0, 10),
        
        # Beauty & Health
        ("skincare serum", 4.0, 8),
        ("masker wajah", 3.5, 10),
        ("essential oil", 4.0, 8),
        
        # Office & Stationery
        ("notebook custom", 3.5, 10),
        ("pulpen", 3.5, 10),
        
        # Food & Beverage
        ("kopi arabica", 4.0, 8),
        ("coklat premium", 4.0, 8),
    ]
    
    agent = SupplierScoutAgent()
    all_results = []
    
    print(f"📋 Will scrape {len(products)} product categories\n")
    
    for i, (product, min_rating, limit) in enumerate(products, 1):
        print(f"[{i}/{len(products)}] 🔍 Scraping: {product}")
        print(f"           Settings: min_rating={min_rating}, limit={limit}")
        
        try:
            suppliers = await agent.find_suppliers(
                product_name=product,
                min_rating=min_rating,
                limit=limit,
                use_apify=False
            )
            
            count = len(suppliers)
            print(f"           ✅ Found {count} suppliers")
            
            if suppliers:
                suppliers_data = [s.model_dump() for s in suppliers]
                all_results.append({
                    "product": product,
                    "count": count,
                    "suppliers": suppliers_data
                })
            
            # Progress
            print(f"           Progress: {i}/{len(products)} ({i/len(products)*100:.1f}%)\n")
            
            # Small delay between scrapes
            if i < len(products):
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"           ❌ Error: {str(e)}\n")
            logger.error(f"Error scraping {product}", exc_info=True)
            continue
    
    # Save all results
    output_dir = Path("./data/bulk_scraping")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save detailed results
    filepath = output_dir / f"bulk_scraping_{timestamp}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            "scraped_at": datetime.now().isoformat(),
            "total_products": len(products),
            "total_suppliers": sum(r['count'] for r in all_results),
            "results": all_results
        }, f, indent=2, ensure_ascii=False, default=str)
    
    # Summary
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║                  Bulk Scraping Complete!                ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")
    
    total_suppliers = sum(r['count'] for r in all_results)
    
    print(f"📊 Summary:")
    print(f"   • Products scraped: {len(all_results)}/{len(products)}")
    print(f"   • Total suppliers found: {total_suppliers}")
    print(f"   • Average per product: {total_suppliers/len(all_results) if all_results else 0:.1f}")
    print()
    
    print(f"📁 Results saved to:")
    print(f"   {filepath}")
    print()
    
    # Top categories
    if all_results:
        print(f"🏆 Top Categories by Supplier Count:")
        sorted_results = sorted(all_results, key=lambda x: x['count'], reverse=True)
        for i, r in enumerate(sorted_results[:5], 1):
            print(f"   {i}. {r['product']}: {r['count']} suppliers")
    
    print()
    return all_results


if __name__ == "__main__":
    try:
        asyncio.run(scrape_bulk_products())
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        logger.error("Fatal error", exc_info=True)
