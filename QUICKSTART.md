# ⚡ Quick Start Guide - TrendScout

Panduan cepat untuk setup dan running TrendScout dalam 5 menit.

## 📋 Prerequisites

- **Python 3.8+** (Check: `python3 --version`)
- **Git** (Check: `git --version`)
- **Internet Connection**

---

## 🚀 Method 1: Quick Start (Recommended)

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/ai-hackthon.git
cd ai-hackthon
```

### Step 2: Install UV (Fast Package Manager)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify
uv --version
```

### Step 3: Setup Virtual Environment & Install Dependencies

```bash
# Create venv
uv venv

# Activate venv
source .venv/bin/activate  # macOS/Linux
# atau
.venv\Scripts\activate     # Windows

# Install dependencies (sangat cepat dengan UV!)
uv pip install -e .
```

### Step 4: Configure API Keys

```bash
# Copy template
cp .env.example .env

# Edit .env dan isi API keys
nano .env  # atau gunakan VS Code, Sublime, dll
```

Minimal configuration (edit `.env`):

```bash
# WAJIB - Get dari https://www.firecrawl.dev/app/api-keys
FIRECRAWL_API_KEY=fc-YOUR-FIRECRAWL-KEY

# WAJIB - Get dari https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-YOUR-OPENAI-KEY

# Optional
APIFY_API_KEY=apify_api_YOUR_KEY
```

### Step 5: Run Application

```bash
# Start server
python app/main.py

# Atau dengan uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Server running at:** http://localhost:8000

✅ **API Docs:** http://localhost:8000/docs

---

## 🐍 Method 2: Traditional Python Setup

### Step 1: Clone & Navigate

```bash
git clone https://github.com/your-org/ai-hackthon.git
cd ai-hackthon
```

### Step 2: Create Virtual Environment

```bash
# Create venv
python3 -m venv .venv

# Activate
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 4: Configure `.env`

```bash
cp .env.example .env
nano .env  # Edit API keys
```

### Step 5: Run

```bash
python app/main.py
```

---

## 🧪 Quick Test

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "firecrawl_configured": true,
  "openai_configured": true
}
```

### Test 2: Simple Query

```bash
curl -X POST "http://localhost:8000/api/agent/execute-workflow?query=carikan%20produk%20terlaris&user_id=test123"
```

### Test 3: Web Interface

1. Open browser: http://localhost:8000/docs
2. Try `/api/agent/execute-workflow` endpoint
3. Input: `query=carikan produk fashion terlaris`

---

## 🎯 Example Usage

### Example 1: Find Bestselling Products

```bash
curl -X POST "http://localhost:8000/api/agent/execute-workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Carikan produk yang paling laris",
    "user_id": "user_123"
  }'
```

### Example 2: Find Suppliers

```bash
curl -X POST "http://localhost:8000/api/agent/find-suppliers" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "skincare serum",
    "user_id": "user_123",
    "location": "Jakarta",
    "min_rating": 4.5,
    "limit": 5
  }'
```

### Example 3: Using Python SDK

```python
import asyncio
from app.agents.super_agent import SuperAgent

async def main():
    agent = SuperAgent()
    
    result = await agent.execute(
        query="Carikan produk fashion yang paling laris",
        user_id="user_123"
    )
    
    print(result)

asyncio.run(main())
```

---

## 🔍 Testing Features

### Test Intent Classification

```bash
python tests/quick_test_bestseller.py
```

Expected output:
```
Query: "Carikan produk yang paling laris"
  ✅ Intent: find_bestsellers (95% confidence)
```

### Test Bestseller Finder

```bash
python tests/test_bestseller_finder.py
```

### Test Supplier Scraping

```bash
python tests/test_bestseller_scraping.py
```

---

## ⚠️ Common Issues

### Issue: `ModuleNotFoundError`

**Solution:**
```bash
# Make sure venv is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: `FIRECRAWL_API_KEY not found`

**Solution:**
```bash
# Verify .env file exists
ls -la .env

# Check content
cat .env | grep FIRECRAWL_API_KEY

# If missing, copy from template
cp .env.example .env
nano .env
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use different port
uvicorn app.main:app --port 8001

# Or kill process
lsof -i :8000  # Find PID
kill -9 <PID>
```

---

## 📚 Next Steps

After successful setup:

1. **Read Full Docs**: [README.md](README.md)
2. **Troubleshooting Guide**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. **Bestseller Feature**: [docs/BESTSELLER_FINDER_FEATURE.md](docs/BESTSELLER_FINDER_FEATURE.md)
4. **API Reference**: http://localhost:8000/docs

---

## 🎓 Learning Path

### Beginner
1. ✅ Complete Quick Start
2. ✅ Test health endpoint
3. ✅ Try example queries via Swagger UI
4. ✅ Read API documentation

### Intermediate
1. ✅ Understand agent architecture
2. ✅ Customize intent classifier
3. ✅ Add new scraping targets
4. ✅ Implement caching

### Advanced
1. ✅ Create custom agents
2. ✅ Integrate new marketplaces
3. ✅ Optimize ranking algorithms
4. ✅ Deploy to production

---

## 📞 Getting Help

- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **GitHub Issues**: [Report Bug](https://github.com/your-org/ai-hackthon/issues)
- **Documentation**: [Full Docs](README.md)

---

## ✅ Checklist

Before proceeding, make sure:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created & activated
- [ ] Dependencies installed (no errors)
- [ ] `.env` file configured with API keys
- [ ] Server starts without errors
- [ ] Health check returns `healthy`
- [ ] Can access http://localhost:8000/docs

**All checked?** 🎉 You're ready to use TrendScout!

---

**Total Setup Time:** ~5 minutes  
**Last Updated:** 2025-11-08
