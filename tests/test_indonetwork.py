#!/usr/bin/env python3
"""
Test script khusus untuk Indonetwork scraping
Jalankan: uv run python test_indonetwork.py
"""

import asyncio
import json
from app.agents.supplier_scout import SupplierScoutAgent

async def test_indonetwork_search():
    """Test pencarian supplier di Indonetwork"""
    print("="*60)
    print("🔍 Test Indonetwork Search")
    print("="*60)
    
    scout = SupplierScoutAgent()
    
    product_name = input("\nMasukkan nama produk (contoh: LED face mask): ").strip()
    if not product_name:
        product_name = "LED face mask"
    
    print(f"\n⏳ Searching Indonetwork for: {product_name}...")
    
    suppliers = await scout._search_indonetwork(product_name, min_rating=4.0)
    
    print(f"\n✅ Found {len(suppliers)} suppliers\n")
    
    for i, supplier in enumerate(suppliers, 1):
        print(f"{i}. {supplier.store_name}")
        print(f"   📍 Location: {supplier.location}")
        print(f"   🏙️  City: {supplier.city}")
        print(f"   📦 Product: {supplier.product_name}")
        print(f"   📊 Min Order: {supplier.minimum_order} pcs")
        
        if supplier.phone:
            print(f"   📞 Phone: {supplier.phone}")
        if supplier.email:
            print(f"   📧 Email: {supplier.email}")
        if supplier.url:
            print(f"   🔗 URL: {supplier.url}")
        
        print()
    
    return suppliers

async def test_company_details():
    """Test mengambil detail lengkap company"""
    print("="*60)
    print("🏢 Test Company Details Extraction")
    print("="*60)
    
    scout = SupplierScoutAgent()
    
    company_url = input("\nMasukkan URL company Indonetwork: ").strip()
    
    if not company_url:
        print("❌ URL tidak boleh kosong")
        return
    
    print(f"\n⏳ Fetching company details from: {company_url}...")
    
    details = await scout._get_indonetwork_company_details(company_url)
    
    if details:
        print("\n✅ Company Details:\n")
        print(json.dumps(details, indent=2, ensure_ascii=False))
    else:
        print("\n❌ Failed to fetch company details")

async def test_batch_scraping():
    """Test batch scraping multiple companies"""
    print("="*60)
    print("📦 Test Batch Scraping Companies")
    print("="*60)
    
    scout = SupplierScoutAgent()
    
    print("\nMasukkan URL companies (pisahkan dengan enter, ketik 'done' untuk selesai):")
    
    urls = []
    while True:
        url = input(f"URL {len(urls)+1}: ").strip()
        if url.lower() == 'done':
            break
        if url:
            urls.append(url)
    
    if not urls:
        print("❌ Tidak ada URL yang dimasukkan")
        return
    
    print(f"\n⏳ Batch scraping {len(urls)} companies...")
    
    companies = await scout.batch_scrape_companies(urls)
    
    print(f"\n✅ Successfully scraped {len(companies)} companies\n")
    
    for i, company in enumerate(companies, 1):
        print(f"{i}. {company.get('company_name', 'Unknown')}")
        print(f"   Contact: {company.get('contact_person', '-')}")
        print(f"   Phone: {company.get('phone', '-')}")
        print(f"   Email: {company.get('email', '-')}")
        print(f"   Address: {company.get('address', '-')}")
        print()
    
    with open("data/batch_companies.json", "w") as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)
    
    print("💾 Full data saved to: data/batch_companies.json")

async def test_category_search():
    """Test search by category"""
    print("="*60)
    print("📂 Test Search by Category")
    print("="*60)
    
    scout = SupplierScoutAgent()
    
    category = input("\nMasukkan kategori (contoh: electronics, beauty, furniture): ").strip()
    if not category:
        category = "electronics"
    
    limit = int(input("Limit hasil (default 10): ").strip() or "10")
    
    print(f"\n⏳ Searching category: {category}...")
    
    suppliers = await scout.search_indonetwork_by_category(category, limit=limit)
    
    print(f"\n✅ Found {len(suppliers)} suppliers in category '{category}'\n")
    
    for i, supplier in enumerate(suppliers, 1):
        print(f"{i}. {supplier.store_name}")
        print(f"   City: {supplier.city}")
        if supplier.phone:
            print(f"   Phone: {supplier.phone}")
        if supplier.email:
            print(f"   Email: {supplier.email}")
        print()

async def test_markdown_export():
    """Test export supplier info to markdown"""
    print("="*60)
    print("📝 Test Markdown Export")
    print("="*60)
    
    scout = SupplierScoutAgent()
    
    company_url = input("\nMasukkan URL company: ").strip()
    
    if not company_url:
        print("❌ URL tidak boleh kosong")
        return
    
    print(f"\n⏳ Exporting to markdown...")
    
    result = await scout.get_indonetwork_supplier_with_markdown(company_url)
    
    if result:
        print("\n✅ Export successful!\n")
        
        print("=" * 60)
        print("MARKDOWN OUTPUT")
        print("=" * 60)
        print(result.get('markdown', 'No markdown content'))
        print()
        
        print("=" * 60)
        print("STRUCTURED DATA")
        print("=" * 60)
        print(json.dumps(result.get('structured_data', {}), indent=2, ensure_ascii=False))
        
        with open("data/supplier_export.md", "w") as f:
            f.write(result.get('markdown', ''))
        
        with open("data/supplier_export.json", "w") as f:
            json.dump(result.get('structured_data', {}), f, indent=2, ensure_ascii=False)
        
        print("\n💾 Files saved:")
        print("   - data/supplier_export.md")
        print("   - data/supplier_export.json")

async def test_full_comparison():
    """Test pencarian supplier dari semua marketplace"""
    print("="*60)
    print("🔍 Test Full Comparison (All Marketplaces)")
    print("="*60)
    
    scout = SupplierScoutAgent()
    
    product_name = input("\nMasukkan nama produk: ").strip()
    if not product_name:
        product_name = "face mask"
    
    print(f"\n⏳ Searching all marketplaces for: {product_name}...")
    print("   - Indonetwork (B2B)")
    print("   - Tokopedia")
    print("   - Shopee")
    print("   - Lazada")
    print()
    
    suppliers = await scout.find_suppliers(
        product_name=product_name,
        min_rating=4.0,
        limit=10
    )
    
    print(f"\n✅ Found {len(suppliers)} suppliers total\n")
    
    by_marketplace = {}
    for supplier in suppliers:
        marketplace = supplier.marketplace
        if marketplace not in by_marketplace:
            by_marketplace[marketplace] = []
        by_marketplace[marketplace].append(supplier)
    
    for marketplace, sups in by_marketplace.items():
        print(f"📊 {marketplace}: {len(sups)} suppliers")
    
    print("\n" + "="*60)
    print("DETAILED RESULTS")
    print("="*60 + "\n")
    
    summary = await scout.generate_search_summary(suppliers)
    print(summary)
    
    with open("data/comparison_results.json", "w") as f:
        json.dump(
            [s.model_dump() for s in suppliers],
            f,
            indent=2,
            default=str,
            ensure_ascii=False
        )
    
    print("💾 Full results saved to: data/comparison_results.json")

def main():
    print("\n🤖 TrendScout - Indonetwork Scraping Test Suite\n")
    print("Select test:")
    print("1. Search Indonetwork")
    print("2. Get Company Details")
    print("3. Batch Scraping")
    print("4. Search by Category")
    print("5. Markdown Export")
    print("6. Full Comparison (All Marketplaces)")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == "1":
        asyncio.run(test_indonetwork_search())
    elif choice == "2":
        asyncio.run(test_company_details())
    elif choice == "3":
        asyncio.run(test_batch_scraping())
    elif choice == "4":
        asyncio.run(test_category_search())
    elif choice == "5":
        asyncio.run(test_markdown_export())
    elif choice == "6":
        asyncio.run(test_full_comparison())
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
