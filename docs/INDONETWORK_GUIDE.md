# 🏭 Indonetwork Scraping Guide

> Comprehensive guide untuk scraping supplier B2B dari Indonetwork.co.id menggunakan Firecrawl

## 🎯 Overview

Indonetwork.co.id adalah platform B2B terbesar di Indonesia yang menghubungkan buyer dengan supplier/perusahaan. Berbeda dengan marketplace consumer (Tokopedia/Shopee), Indonetwork fokus pada:

- **B2B Transactions** - Bulk orders, wholesale
- **Complete Company Info** - Alamat lengkap, contact person, email, phone
- **Product Categories** - Organized by industry categories
- **Verified Suppliers** - Company profiles with business details

## 🚀 Features

### 1. Search Suppliers by Product Name

Cari supplier berdasarkan nama produk dengan ekstraksi kontak lengkap:

```python
from app.agents.supplier_scout import SupplierScoutAgent

scout = SupplierScoutAgent()

suppliers = await scout._search_indonetwork(
    product_name="LED face mask",
    min_rating=4.0
)

for supplier in suppliers:
    print(f"Company: {supplier.store_name}")
    print(f"Phone: {supplier.phone}")
    print(f"Email: {supplier.email}")
    print(f"Address: {supplier.location}")
```

### 2. Get Detailed Company Information

Dapatkan informasi lengkap perusahaan dari halaman company:

```python
company_url = "https://www.indonetwork.co.id/company-name"

details = await scout._get_indonetwork_company_details(company_url)

# Output includes:
# - company_name
# - contact_person
# - phone (all numbers)
# - mobile
# - email
# - website
# - complete address
# - city, province, postal_code
# - products list
# - business_type
# - year_established
# - employee_count
```

### 3. Batch Scraping Multiple Companies

Scrape multiple company pages secara parallel:

```python
company_urls = [
    "https://www.indonetwork.co.id/company1",
    "https://www.indonetwork.co.id/company2",
    "https://www.indonetwork.co.id/company3"
]

companies = await scout.batch_scrape_companies(company_urls)

# Returns list of complete company data
print(f"Scraped {len(companies)} companies")
```

### 4. Search by Category

Cari supplier berdasarkan kategori produk:

```python
suppliers = await scout.search_indonetwork_by_category(
    category="electronics",
    limit=10
)

# Supported categories:
# - electronics
# - beauty
# - furniture
# - fashion
# - industrial
# - machinery
# - chemicals
# etc.
```

### 5. Export to Markdown

Export company info ke markdown format untuk dokumentasi:

```python
result = await scout.get_indonetwork_supplier_with_markdown(company_url)

markdown_content = result['markdown']
structured_data = result['structured_data']
metadata = result['metadata']

# Save to file
with open("supplier_report.md", "w") as f:
    f.write(markdown_content)
```

## 📡 API Endpoints

### POST /api/agent/indonetwork/search

Search Indonetwork by product name.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/agent/indonetwork/search?product_name=LED%20face%20mask&min_rating=4.0"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "suppliers": [
      {
        "name": "PT Beauty Indonesia",
        "store_name": "PT Beauty Indonesia",
        "phone": "+62-21-1234567",
        "email": "sales@beauty.co.id",
        "location": "Jl. Sudirman No. 123, Jakarta Selatan",
        "city": "Jakarta",
        "product_name": "LED Face Mask",
        "minimum_order": 10,
        "url": "https://www.indonetwork.co.id/pt-beauty-indonesia",
        "marketplace": "Indonetwork"
      }
    ],
    "count": 5
  }
}
```

### POST /api/agent/indonetwork/batch-scrape

Batch scrape multiple company URLs.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/agent/indonetwork/batch-scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "company_urls": [
      "https://www.indonetwork.co.id/company1",
      "https://www.indonetwork.co.id/company2"
    ]
  }'
```

### GET /api/agent/indonetwork/company-details

Get detailed company information.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/agent/indonetwork/company-details?company_url=https://www.indonetwork.co.id/company-name"
```

### GET /api/agent/indonetwork/category/{category}

Search by category.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/agent/indonetwork/category/electronics?limit=10"
```

### GET /api/agent/indonetwork/export-markdown

Export to markdown format.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/agent/indonetwork/export-markdown?company_url=https://www.indonetwork.co.id/company-name"
```

## 🧪 Testing

### Interactive Test Script

```bash
uv run python test_indonetwork.py
```

**Available Tests:**
1. Search Indonetwork
2. Get Company Details
3. Batch Scraping
4. Search by Category
5. Markdown Export
6. Full Comparison (All Marketplaces)

### Example Test Session

```bash
$ uv run python test_indonetwork.py

🤖 TrendScout - Indonetwork Scraping Test Suite

Select test:
1. Search Indonetwork
2. Get Company Details
3. Batch Scraping
4. Search by Category
5. Markdown Export
6. Full Comparison (All Marketplaces)

Enter choice (1-6): 1

Masukkan nama produk (contoh: LED face mask): skincare
⏳ Searching Indonetwork for: skincare...

✅ Found 5 suppliers

1. PT Kosmetik Indonesia
   📍 Location: Jl. Gatot Subroto No. 45, Jakarta Selatan, DKI Jakarta 12930
   🏙️  City: Jakarta
   📦 Product: Skincare Products
   📊 Min Order: 50 pcs
   📞 Phone: +62-21-5234567
   📧 Email: info@kosmetik.co.id
   🔗 URL: https://www.indonetwork.co.id/pt-kosmetik-indonesia
```

## 🔥 Firecrawl Integration

Indonetwork scraping menggunakan Firecrawl dengan:

### 1. Browser Actions

```python
actions = [
    {"type": "wait", "milliseconds": 3000},
    {"type": "scroll", "y": 1500},
    {"type": "wait", "milliseconds": 1500}
]

result = await firecrawl.scrape_with_actions(
    url,
    actions=actions,
    formats=[...]
)
```

**Why Actions?**
- Wait untuk load dynamic content
- Scroll untuk trigger lazy loading
- Multiple waits untuk ensure semua data loaded

### 2. Structured JSON Extraction

```python
formats=[{
    "type": "json",
    "prompt": """Extract complete company information:
    - company_name
    - contact_person
    - phone (all phone numbers)
    - email
    - address
    - products
    - business_type
    """
}]
```

**Firecrawl AI** automatically extracts structured data dari HTML.

### 3. Crawling for Category Search

```python
result = await firecrawl.crawl(
    category_url,
    limit=10,
    formats=["json"]
)
```

Crawl multiple pages dalam satu category.

### 4. Multiple Format Support

```python
formats=["markdown", {
    "type": "json",
    "prompt": "Extract all information"
}]
```

Dapatkan:
- **Markdown** untuk human-readable reports
- **JSON** untuk structured data processing

## 📊 Data Structure

### Supplier Object

```python
Supplier(
    name="PT Beauty Indonesia",
    store_name="PT Beauty Indonesia",
    rating=4.5,
    location="Jl. Sudirman No. 123, Jakarta Selatan, DKI Jakarta 12930",
    city="Jakarta",
    product_name="LED Face Mask",
    price=0.0,  # B2B negotiable
    currency="IDR",
    stock_available=True,
    minimum_order=10,
    url="https://www.indonetwork.co.id/pt-beauty-indonesia",
    phone="+62-21-1234567",
    email="sales@beauty.co.id",
    marketplace="Indonetwork",
    verified=True,
    response_rate=80.0
)
```

### Company Details Object

```json
{
  "company_name": "PT Beauty Indonesia",
  "contact_person": "John Doe",
  "phone": ["+62-21-1234567", "+62-21-7654321"],
  "mobile": "+62-812-3456-7890",
  "email": "sales@beauty.co.id",
  "website": "https://beauty.co.id",
  "address": "Jl. Sudirman No. 123, Jakarta Selatan",
  "city": "Jakarta",
  "province": "DKI Jakarta",
  "postal_code": "12930",
  "products": [
    "LED Face Mask",
    "Skincare Products",
    "Beauty Devices"
  ],
  "business_type": "Manufacturer",
  "year_established": 2010,
  "employee_count": "50-100",
  "main_products": "Beauty & Cosmetics",
  "description": "Leading manufacturer of beauty devices..."
}
```

## 🎯 Use Cases

### 1. B2B Sourcing

Find verified suppliers with complete contact info untuk bulk orders:

```python
suppliers = await scout.find_suppliers(
    product_name="smartphone accessories",
    min_rating=4.0,
    limit=10
)

# Filter by location
jakarta_suppliers = [
    s for s in suppliers 
    if s.marketplace == "Indonetwork" and "Jakarta" in s.city
]
```

### 2. Market Research

Analyze suppliers by category:

```python
electronics = await scout.search_indonetwork_by_category("electronics", 20)
fashion = await scout.search_indonetwork_by_category("fashion", 20)

print(f"Electronics suppliers: {len(electronics)}")
print(f"Fashion suppliers: {len(fashion)}")
```

### 3. Lead Generation

Batch scrape companies untuk sales leads:

```python
# Get company URLs from search
search_result = await scout._search_indonetwork("industrial machinery", 4.0)
company_urls = [s.url for s in search_result]

# Scrape detailed info
companies = await scout.batch_scrape_companies(company_urls)

# Export to CSV for CRM
import csv
with open('leads.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=companies[0].keys())
    writer.writeheader()
    writer.writerows(companies)
```

### 4. Supplier Documentation

Generate supplier reports:

```python
result = await scout.get_indonetwork_supplier_with_markdown(company_url)

# Generate PDF report
from markdown2 import markdown
html = markdown(result['markdown'])
# Convert to PDF...
```

## ⚡ Performance

- **Search**: ~5-10 seconds per search query
- **Company Details**: ~3-5 seconds per company
- **Batch Scraping**: Parallel, ~5 seconds for 5 companies
- **Category Search**: ~10-15 seconds for 10 results

**Optimization Tips:**
- Use batch scraping untuk multiple companies
- Cache results untuk 24 hours
- Use async/await untuk parallel requests

## 🛡️ Best Practices

### 1. Rate Limiting

```python
import asyncio

# Add delay between requests
for url in urls:
    result = await scout._get_indonetwork_company_details(url)
    await asyncio.sleep(1)  # 1 second delay
```

### 2. Error Handling

```python
try:
    suppliers = await scout._search_indonetwork(product_name, 4.0)
except Exception as e:
    logger.error(f"Search failed: {e}")
    # Fallback to other marketplaces
    suppliers = await scout._search_tokopedia(product_name, 4.0)
```

### 3. Data Validation

```python
# Validate phone numbers
def is_valid_phone(phone: str) -> bool:
    return phone and (phone.startswith('+62') or phone.startswith('0'))

# Validate email
import re
def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

## 🔍 Troubleshooting

### Issue: "No suppliers found"

**Solution:**
- Check product name spelling
- Try broader search terms
- Verify Firecrawl API key

### Issue: "Company details empty"

**Solution:**
- Increase wait time in actions
- Check if URL is correct
- Some companies may not have complete info

### Issue: "Scraping too slow"

**Solution:**
- Use batch scraping
- Reduce limit parameter
- Cache results

## 📝 Example: Complete Workflow

```python
# 1. Search suppliers
suppliers = await scout._search_indonetwork("LED face mask", 4.0)

# 2. Get detailed info for top 3
company_urls = [s.url for s in suppliers[:3]]
details = await scout.batch_scrape_companies(company_urls)

# 3. Generate reports
for i, company in enumerate(details):
    report = await scout.get_indonetwork_supplier_with_markdown(company_urls[i])
    
    with open(f"supplier_{i+1}_report.md", "w") as f:
        f.write(report['markdown'])
    
    print(f"Report generated: supplier_{i+1}_report.md")

# 4. Send to outreach agent
from app.agents.outreach_agent import OutreachAgent

outreach = OutreachAgent()
messages = await outreach.contact_suppliers(
    product_name="LED face mask",
    quantity=50,
    suppliers=suppliers[:3],
    channels=["email"]
)

print(f"Contacted {len(messages)} suppliers")
```

## 🎉 Summary

Indonetwork scraping provides:
- ✅ **Complete contact info** (phone, email, address)
- ✅ **B2B focus** (bulk orders, wholesale)
- ✅ **Verified suppliers** (company profiles)
- ✅ **Multiple scraping methods** (search, category, batch)
- ✅ **Export options** (JSON, Markdown)
- ✅ **Integration ready** (API endpoints)

Perfect untuk **B2B sourcing, lead generation, market research**! 🚀
