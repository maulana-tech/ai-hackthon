# TrendScout Quick Start Guide

## 🚀 Setup in 5 Minutes

### 1. Clone & Install Dependencies

```bash
# Install UV package manager (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
vim .env  # or nano .env
```

### 3. Required API Keys

#### Essential (Required):

**OpenRouter API Key** (for AI Agent)
- Get from: https://openrouter.ai/keys
- Add to `.env`:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
LLM_PROVIDER=openrouter
LLM_MODEL=qwen/qwen-2.5-coder-32b-instruct
```

**Firecrawl API Key** (for web scraping)
- Get from: https://firecrawl.dev
- Add to `.env`:
```bash
FIRECRAWL_API_KEY=fc-your-api-key
```

#### Optional (For Full Features):

**GetCirclo** (for WhatsApp integration)
```bash
GETCIRCLO_JWT_TOKEN=your-jwt-token
GETCIRCLO_API_KEY=your-api-key
```

**Apify** (for marketplace scraping)
```bash
APIFY_API_KEY=your-apify-key
```

### 4. Test Configuration

```bash
# Test LLM configuration
uv run python test_qwen_config.py

# Test intent classifier
uv run python test_intent_only.py

# Test scraping
uv run python scrape_real_suppliers.py
```

### 5. Run the Application

```bash
# Start FastAPI server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API available at: http://localhost:8000

## 📝 Minimal .env File

For basic testing, you only need:

```bash
# LLM (Required)
OPENROUTER_API_KEY=sk-or-v1-your-key
LLM_PROVIDER=openrouter
LLM_MODEL=qwen/qwen-2.5-coder-32b-instruct

# Scraping (Required)
FIRECRAWL_API_KEY=fc-your-key

# Optional - can leave blank for testing
GETCIRCLO_JWT_TOKEN=
GETCIRCLO_API_KEY=
APIFY_API_KEY=
OPENAI_API_KEY=
RAPIDAPI_KEY=

# Email (for outreach - optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=

# Twilio (for WhatsApp - optional)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_NUMBER=

# Database
DATABASE_URL=sqlite:///./data/trendscout.db
REDIS_URL=redis://localhost:6379/0
```

## 🧪 Test Workflows

### Test 1: Intent Classification

```bash
uv run python test_intent_only.py
```

Expected output:
```
✅ Intent: find_suppliers
✅ Confidence: 0.90
✅ Parameters: {"product_name": "tas macrame"}
```

### Test 2: Supplier Scraping

```bash
uv run python scrape_real_suppliers.py
```

Expected output:
```
✅ Found 5 suppliers
💾 Saved to: data/suppliers/suppliers_*.json
```

### Test 3: Super Agent

```bash
uv run python -c "
import asyncio
from app.agents.super_agent import SuperAgent

async def test():
    agent = SuperAgent()
    result = await agent.execute(
        query='Cari supplier tas macrame',
        user_id='test_user'
    )
    print(result)

asyncio.run(test())
"
```

## 📚 Next Steps

1. ✅ Read `DOCS_INDEX.md` for full documentation
2. ✅ Review `BUILD_AGENT.md` for agent architecture
3. ✅ Check `WHY_QWEN_CODER.md` for LLM model details
4. ✅ See `OPENROUTER_SETUP.md` for advanced LLM config

## 🐛 Troubleshooting

### Error: "No LLM API key configured"
**Solution:** Add OpenRouter key to `.env`:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key
```

### Error: "Firecrawl API error"
**Solution:** Check Firecrawl API key is valid and has credits

### Error: "Module not found"
**Solution:** Reinstall dependencies:
```bash
uv pip install -r requirements.txt
```

### Fallback to Keyword Classification
This is **normal** when:
- OpenRouter API key not configured
- API quota exceeded
- Network error

The system will still work using keyword-based intent classification (70% accuracy vs 95% with LLM).

## 💡 Tips

1. **Start Small**: Test with intent classifier first before full scraping
2. **Monitor Costs**: Check https://openrouter.ai/activity for API usage
3. **Use Qwen Coder**: Cheapest model with best structured output
4. **Check Logs**: All logs saved to `logs/` directory

## 📞 Support

- **Documentation**: See `DOCS_INDEX.md`
- **Issues**: Check error logs in `logs/`
- **API Status**: https://openrouter.ai/status

## 🎯 Quick Commands

```bash
# Test everything
uv run python test_intent_only.py
uv run python scrape_real_suppliers.py

# Start server
uv run uvicorn app.main:app --reload

# Run bulk scraping
uv run python scrape_bulk_data.py

# Check configuration
uv run python test_qwen_config.py
```

---

**Ready to start!** 🚀

Copy `.env.example` to `.env`, add your OpenRouter and Firecrawl keys, then run tests!
