# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview
TrendScout Supplier Connector is a Super AI-Agent system that connects global trend analysis with Indonesian suppliers using Firecrawl API and GetCirclo Platform.

## Development Commands

### Environment Setup
```bash
# Install UV package manager (fast Python package management)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate      # Windows

# Install all dependencies
uv pip install -e .

# Setup environment variables
cp .env.example .env
# Edit .env with required API keys
```

### Running the Application
```bash
# Start FastAPI server with hot reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Alternative: Direct Python execution
uv run python app/main.py

# API Documentation available at: http://localhost:8000/docs
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app tests/

# Run specific test file
uv run pytest tests/test_bestseller_finder.py

# Skip slow tests
uv run pytest -m "not slow"

# Run specific test function
uv run pytest tests/test_bestseller_finder.py::test_intent_classification
```

### Code Quality
```bash
# Format code with Black
uv run black app/ tests/

# Lint with Ruff
uv run ruff check app/ tests/

# Type checking with mypy
uv run mypy app/
```

## Architecture Overview

### Multi-Agent System
The codebase implements a sophisticated multi-agent architecture orchestrated by a Super Agent:

```
Super Agent (app/agents/super_agent.py)
├── Trend Analyst Agent (app/agents/trend_analyst.py)
│   └── Analyzes global product trends via Firecrawl API
├── Supplier Scout Agent (app/agents/supplier_scout.py)
│   └── Searches Indonesian marketplaces (Tokopedia, Shopee, Lazada)
├── Outreach Agent (app/agents/outreach_agent.py)
│   └── Contacts suppliers via WhatsApp/Email
└── Memory Keeper Agent (app/agents/memory_keeper.py)
    └── Manages user preferences and history
```

### Core Integration Points

#### Firecrawl Integration (app/integrations/firecrawl_client.py)
- Web scraping with structured data extraction
- Supports JSON schemas for data parsing
- Browser actions (scroll, wait, screenshot)
- Batch URL processing

#### GetCirclo Platform (app/integrations/getcirclo_client.py)
- WhatsApp messaging API
- Memory persistence
- Agent orchestration

#### Additional APIs
- **OpenRouter/OpenAI**: LLM provider (configured in app/config.py)
- **RapidAPI**: Lazada marketplace data
- **Apify**: Alternative scraping service
- **Twilio**: WhatsApp/SMS messaging

### API Routing Structure
- **Main router**: app/main.py
- **Agent endpoints**: app/routes/agent_routes.py
- **Circlo integration**: app/routes/circlo.py

### Data Models
- **Pydantic schemas**: app/models/schemas.py
- Request/response validation
- Supplier, Product, and Trend data structures

## Key Workflows

### 1. Full Trend-to-Supplier Pipeline
```python
POST /api/agent/execute-workflow
# Orchestrates: trend analysis → supplier search → contact generation
```

### 2. Marketplace Scraping
```python
POST /api/agent/find-suppliers
# Uses Firecrawl to scrape Tokopedia/Shopee/Lazada
```

### 3. Indonetwork B2B Integration
```python
POST /api/agent/indonetwork/search
# Specialized B2B supplier scraping with complete contact info
```

## Configuration Management

### Environment Variables (.env)
```
FIRECRAWL_API_KEY       # Required for web scraping
GETCIRCLO_API_KEY       # Required for platform integration
OPENROUTER_API_KEY      # LLM provider (or OPENAI_API_KEY)
RAPIDAPI_KEY           # Marketplace APIs
APIFY_API_KEY          # Alternative scraping
```

### LLM Configuration
- Default model: qwen/qwen-2.5-coder-32b-instruct
- Provider: OpenRouter (configurable to OpenAI)
- Set in app/config.py: `llm_provider` and `llm_model`

## Data Storage
- **SQLite database**: data/trendscout.db
- **User memory**: data/memory/{user_id}.json
- **Logs**: logs/app.log
- **Bulk scraping cache**: data/scraped/

## Error Handling Patterns
- Retry logic with exponential backoff (using tenacity)
- Graceful fallbacks for API failures
- Comprehensive logging throughout agents
- Global exception handler in FastAPI

## Development Scripts
- `scripts/example_usage.py` - API usage examples
- `scripts/run_agent_with_circlo.py` - Circlo platform integration
- `scripts/scrape_real_suppliers.py` - Direct supplier scraping
- `scripts/setup_circlo_agents.py` - Agent configuration

## Testing Considerations
- Async test support with pytest-asyncio
- Mock external API calls to avoid rate limits
- Test data fixtures in tests/fixtures/
- Integration tests require valid API keys

## Performance Optimization
- Response caching (24-hour TTL)
- Parallel scraping for multiple URLs
- Connection pooling for HTTP requests
- Async/await throughout for non-blocking I/O