# Changelog

## [1.1.0] - Indonetwork Integration - 2024-11-08

### 🎉 Added - Indonetwork.co.id B2B Scraping

#### New Features
- **Indonetwork Search**: Cari supplier B2B dengan contact lengkap (phone, email, address)
- **Company Details Extraction**: Scrape informasi lengkap perusahaan (business type, products, employee count, dll)
- **Batch Scraping**: Scrape multiple company URLs secara parallel
- **Category Search**: Cari supplier berdasarkan kategori produk
- **Markdown Export**: Export company info ke markdown format untuk dokumentasi

#### New API Endpoints
- `POST /api/agent/indonetwork/search` - Search suppliers by product name
- `POST /api/agent/indonetwork/batch-scrape` - Batch scrape companies
- `GET /api/agent/indonetwork/company-details` - Get detailed company info
- `GET /api/agent/indonetwork/category/{category}` - Search by category
- `GET /api/agent/indonetwork/export-markdown` - Export to markdown

#### New Methods in SupplierScoutAgent
- `_search_indonetwork()` - Search Indonetwork with actions
- `_get_indonetwork_company_details()` - Get detailed company info
- `batch_scrape_companies()` - Batch scrape multiple URLs
- `search_indonetwork_by_category()` - Search by category
- `get_indonetwork_supplier_with_markdown()` - Export to markdown

#### New Files
- `test_indonetwork.py` - Interactive test suite for Indonetwork
- `INDONETWORK_GUIDE.md` - Comprehensive documentation

#### Updated Files
- `app/agents/supplier_scout.py` - Added Indonetwork integration
- `app/routes/agent_routes.py` - Added 5 new endpoints
- `README.md` - Updated with Indonetwork info

### 🔥 Firecrawl Usage
- Browser actions (wait, scroll) untuk dynamic content
- Structured JSON extraction dengan AI prompts
- Multiple format support (markdown + JSON)
- Parallel batch scraping

### 📊 Data Extracted
From Indonetwork company pages:
- Company name
- Contact person
- Phone numbers (all)
- Mobile number
- Email address
- Website URL
- Complete address (street, city, province, postal code)
- Products list
- Business type
- Year established
- Employee count
- Company description

### 🎯 Use Cases
1. **B2B Sourcing** - Find verified suppliers dengan contact lengkap
2. **Lead Generation** - Batch scrape untuk sales leads
3. **Market Research** - Analyze suppliers by category
4. **Supplier Documentation** - Generate supplier reports

### 🧪 Testing
```bash
# Interactive test
uv run python test_indonetwork.py

# Options:
# 1. Search Indonetwork
# 2. Get Company Details
# 3. Batch Scraping
# 4. Search by Category
# 5. Markdown Export
# 6. Full Comparison
```

### 📈 Performance
- Search: ~5-10 seconds
- Company Details: ~3-5 seconds
- Batch Scraping: ~5 seconds for 5 companies (parallel)

---

## [1.0.0] - Initial Release - 2024-11-08

### 🎉 Initial Features

#### Core Agents
- **Super Agent** - Orchestrator
- **Trend Analyst Agent** - Google Trends, TikTok, Amazon scraping
- **Supplier Scout Agent** - Tokopedia, Shopee, Lazada scraping
- **Outreach Agent** - WhatsApp & Email automation
- **Memory Keeper Agent** - User preferences & history

#### API Endpoints
- Full workflow execution
- Trend analysis
- Supplier search
- Contact suppliers
- Job status tracking
- User history & insights

#### Tech Stack
- FastAPI + Uvicorn
- UV package manager
- Firecrawl API
- Pytrends
- Twilio (WhatsApp)
- SMTP (Email)

#### Documentation
- README.md
- QUICKSTART.md
- AGENTS.md
- FIRECRAWL.md
- PRD.md

#### Testing
- `test_agent.py` - Interactive test suite
- `example_usage.py` - API examples

#### Deployment
- Docker support
- UV package manager
- Environment configuration

---

## Future Releases

### [1.2.0] - Marketing Swarm (Planned)
- Campaign Planner Agent
- Content Creator Agent
- Ad Manager Agent
- Engager Bot Agent
- Instagram/TikTok integration

### [1.3.0] - Advanced Features (Planned)
- AI-powered supplier ranking
- Price comparison & negotiation
- Automated purchase orders
- Supplier performance tracking
- Multi-language support

---

## Migration Guide

### From 1.0.0 to 1.1.0

No breaking changes! Semua existing code tetap berfungsi.

**New Features:**
1. Add Indonetwork to supplier search automatically
2. Use new Indonetwork endpoints untuk advanced features
3. Update environment variables (optional - Indonetwork tidak perlu extra API key)

**Example:**
```python
# Old way (still works)
suppliers = await scout.find_suppliers("LED mask", limit=5)

# Now includes Indonetwork suppliers automatically!
# Indonetwork suppliers have: phone, email, complete address

# New way (Indonetwork only)
suppliers = await scout._search_indonetwork("LED mask", 4.0)
```

---

## Feedback & Contributions

Feedback welcome! Open an issue atau PR di GitHub.
