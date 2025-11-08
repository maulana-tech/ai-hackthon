# 🚀 Quick Start Guide - TrendScout Supplier Connector

## Langkah Cepat (5 Menit)

### 1. Install UV Package Manager

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart terminal atau jalankan:
source $HOME/.cargo/env
```

### 2. Setup Project

```bash
# Masuk ke directory project
cd ai-hackthon

# Buat virtual environment
uv venv

# Activate venv
source .venv/bin/activate  # macOS/Linux
# atau
.venv\Scripts\activate     # Windows

# Install dependencies (sangat cepat dengan uv!)
uv pip install -e .
```

### 3. Konfigurasi API Keys

```bash
# Copy template
cp .env.example .env

# Edit .env dan isi API keys (minimal yang ini):
nano .env
```

**Required API Keys:**

```env
FIRECRAWL_API_KEY=fc-YOUR-API-KEY           # https://firecrawl.dev
GETCIRCLO_API_KEY=your-getcirclo-api-key    # https://getcirclo.com
OPENAI_API_KEY=sk-your-openai-api-key       # https://platform.openai.com
```

**Optional (untuk fitur lengkap):**

```env
RAPIDAPI_KEY=your-rapidapi-key              # Untuk Lazada API
TWILIO_ACCOUNT_SID=your-sid                 # Untuk WhatsApp
TWILIO_AUTH_TOKEN=your-token
SMTP_USERNAME=your-email@gmail.com          # Untuk Email
SMTP_PASSWORD=your-app-password
```

### 4. Jalankan Server

**Opsi 1: Menggunakan script (Recommended)**
```bash
./run.sh
```

**Opsi 2: Manual**
```bash
uv run python app/main.py
```

**Opsi 3: Dengan uvicorn**
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di: **http://localhost:8000**

### 5. Test API

**Buka browser:**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

**Atau gunakan curl:**
```bash
curl http://localhost:8000/health
```

## 🎯 Cara Menggunakan

### Test Script Interaktif

```bash
uv run python test_agent.py
```

Pilih:
1. **Full Workflow** - Test lengkap dari trend analysis sampai supplier
2. Trend Analysis Only
3. Supplier Search Only

### Example API Usage

```bash
uv run python example_usage.py
```

### cURL Examples

**1. Full Workflow (Main Feature)**
```bash
curl -X POST "http://localhost:8000/api/agent/execute-workflow?query=skincare%20products&user_id=user123&quantity=20&auto_contact=false"
```

**2. Analyze Trends**
```bash
curl -X POST "http://localhost:8000/api/agent/analyze-trend" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "smart home devices",
    "user_id": "user123",
    "region": "global",
    "limit": 3
  }'
```

**3. Find Suppliers**
```bash
curl -X POST "http://localhost:8000/api/agent/find-suppliers" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "LED face mask",
    "user_id": "user123",
    "min_rating": 4.0,
    "limit": 5
  }'
```

## 🐳 Docker (Alternative)

```bash
# Build dan run dengan docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

## 📊 Expected Results

### Workflow Output Example:

```
✅ WORKFLOW COMPLETED!
================================

📊 Job ID: 550e8400-e29b-41d4-a716-446655440000

🔍 Trending Products Found: 3

  1. LED Face Mask
     Category: beauty
     Trend Score: 85.5/100
     Growth: +120.5%
     Platform: TikTok
     Search Volume: 150,000

🏪 Suppliers Found: 5

  1. Beauty Supplier Jakarta
     Marketplace: Tokopedia
     Location: Jakarta
     Rating: 4.8/5.0
     Price: Rp 250,000
     Min Order: 10 pcs
     Stock: ✓ Available

📧 Outreach Messages: 0
(Set auto_contact=true to enable)
```

## 🔧 Troubleshooting

### Error: "uv: command not found"

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Atau restart terminal
```

### Error: "FIRECRAWL_API_KEY not set"

```bash
# Edit .env file
nano .env

# Atau export langsung
export FIRECRAWL_API_KEY="fc-your-api-key"
```

### Error: "No module named 'app'"

```bash
# Make sure you're in project root
cd ai-hackthon

# Reinstall
uv pip install -e .
```

### Error: "Port 8000 already in use"

```bash
# Check what's using port 8000
lsof -i :8000

# Kill process or use different port
uv run uvicorn app.main:app --port 8001
```

## 📝 Next Steps

1. ✅ Test API dengan `test_agent.py`
2. ✅ Explore API docs di `/docs`
3. ✅ Baca `README.md` untuk dokumentasi lengkap
4. ✅ Cek `AGENTS.md` untuk arsitektur agents
5. ✅ Deploy ke GetCirclo Platform

## 🎓 Documentation

- **README.md** - Dokumentasi lengkap
- **AGENTS.md** - Agent architecture & tasks
- **FIRECRAWL.md** - Firecrawl API guide
- **PRD.md** - Product requirements

## 🆘 Need Help?

- Check API docs: http://localhost:8000/docs
- Run test script: `uv run python test_agent.py`
- Check logs: `tail -f logs/*.log`

## 🎉 Ready to Deploy!

Project ini sudah siap untuk:
- ✅ Local development
- ✅ Testing lengkap
- ✅ Docker deployment
- ✅ GetCirclo Platform integration

Selamat menggunakan TrendScout! 🚀
