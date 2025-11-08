# TrendScout Scripts

This folder contains utility and operational scripts.

## 📂 Scripts Overview

### Scraping Scripts

**scrape_real_suppliers.py** - Production supplier scraper
- Scrapes real suppliers from Indonetwork
- Saves to JSON and CSV
- Configurable products and filters
```bash
uv run python scripts/scrape_real_suppliers.py
```

**scrape_bulk_data.py** - Bulk scraping for multiple categories
- Scrapes 17 product categories
- Batch processing
- Progress tracking
```bash
uv run python scripts/scrape_bulk_data.py
```

### Setup Scripts

**setup_circlo_agents.py** - Circlo agent registration
- Registers TrendScout agents to Circlo platform
- Configures webhooks
- Sets up agent profiles
```bash
uv run python scripts/setup_circlo_agents.py
```

### Example Scripts

**example_usage.py** - Usage examples
- Demonstrates API usage
- Shows agent workflows
- Example queries
```bash
uv run python scripts/example_usage.py
```

## 🚀 Quick Commands

```bash
# Run from project root
cd /Users/em/web/ai-hackthon

# Scrape suppliers
uv run python scripts/scrape_real_suppliers.py

# Bulk scraping
uv run python scripts/scrape_bulk_data.py

# Setup Circlo
uv run python scripts/setup_circlo_agents.py

# View examples
uv run python scripts/example_usage.py
```

## 📁 Output Locations

- Scraped data: `../data/suppliers/`
- Bulk data: `../data/bulk_scraping/`
- Logs: `../logs/`

## 🔧 Configuration

All scripts use environment variables from `.env` file in project root.

Required:
- `FIRECRAWL_API_KEY` - For scraping
- `OPENROUTER_API_KEY` - For AI features
- `GETCIRCLO_JWT_TOKEN` - For Circlo integration (optional)

Back to [Main README](../README.md)
