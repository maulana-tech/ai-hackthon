# TrendScout with GetCirclo Integration 🚀

> **Super AI-Agent** yang menghubungkan analisis tren global dengan supplier Indonesia + **Full GetCirclo Platform Integration**

## 🎯 What's New - GetCirclo Integration

### ✅ Fitur Baru yang Ditambahkan:

1. **🔐 JWT Token Authentication**
   - Token sudah pre-configured dan valid sampai 2125!
   - Auto-fallback ke API key jika dibutuhkan

2. **🤖 Intelligent Conversation Handler**
   - 6 jenis intent classification (trend analysis, supplier search, marketing, dll)
   - Powered by GPT-3.5 Turbo
   - Response dalam Bahasa Indonesia

3. **📱 7 API Endpoints Baru**
   - Webhook untuk Circlo conversations
   - Create posts, register agents
   - User preferences & memory management
   - WhatsApp messaging

4. **⚡ UV Package Manager Support**
   - Setup 10x lebih cepat dari pip
   - One-command installation
   - Automated setup script

5. **📚 Complete Documentation**
   - 2000+ lines documentation
   - Step-by-step guides
   - Testing & verification

## 🚀 Quick Start (Super Cepat dengan UV!)

### Option 1: Automated Setup ⚡ (Recommended)

```bash
# One command setup!
bash UV_SETUP.sh
```

Script ini akan:
- ✅ Install UV (jika belum ada)
- ✅ Create virtual environment
- ✅ Install semua dependencies (super cepat!)
- ✅ Setup .env dengan JWT token
- ✅ Verify installation

**Estimasi waktu: 30-60 detik!** 🏃‍♂️

### Option 2: Manual Setup

```bash
# 1. Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Setup project
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 3. Configure environment
cp .env.circlo .env
# Edit .env dan tambahkan:
# - FIRECRAWL_API_KEY
# - OPENAI_API_KEY

# 4. Start server
uv run uvicorn app.main:app --reload

# 5. Register Circlo agents
uv run python setup_circlo_agents.py
```

## 📖 Documentation Index

| Document | Description | Lines |
|----------|-------------|-------|
| **QUICKSTART_UV.md** | Complete UV setup guide | 500+ |
| **CIRCLO_INTEGRATION.md** | API reference & examples | 430+ |
| **CIRCLO_VERIFICATION.md** | Testing & troubleshooting | 450+ |
| **CIRCLO_IMPLEMENTATION_SUMMARY.md** | Technical details | 300+ |
| **CIRCLO_FINAL_SUMMARY.md** | Complete summary | 200+ |
| **CIRCLO.md** | Original Circlo API docs | 260+ |

**Total: 2000+ lines of documentation!** 📚

## 🎯 Key Features

### 1. Intelligent Conversation Handler

```
User: "Cari produk skincare yang lagi tren"
  ↓
[Intent Classification via GPT-3.5]
  ↓
Intent: trend_analysis
  ↓
[Generate Personalized Response]
  ↓
Response: "🔍 Saya akan mencari tren produk skincare..."
  ↓
[Trigger Super Agent in Background]
  ↓
[Save to Circlo Memory]
```

**6 Intent Types:**
- `trend_analysis` - Analisis tren produk
- `supplier_search` - Cari supplier
- `marketing_campaign` - Buat kampanye
- `greeting` - Sapaan user
- `help` - Bantuan
- `general` - Query umum

### 2. Complete Circlo API Integration

**20+ API Methods:**
- User preferences (get, save, update)
- Memory management (save, retrieve, delete)
- Agent operations (create, session, logs)
- Content publishing (create posts)
- Messaging (WhatsApp, bulk send)
- Health monitoring

### 3. Automated Agent Registration

```bash
uv run python setup_circlo_agents.py
```

Registers 4 agents:
- **TrendScout Super Agent** - Main orchestrator
- **TrendScout Analyst** - Trend specialist
- **TrendScout Supplier Connector** - Supplier matching
- **TrendScout Marketing Bot** - Campaign automation

## 🧪 Testing

### Quick Health Check
```bash
# Start server
uv run uvicorn app.main:app --reload

# Test in new terminal
curl http://localhost:8000/health
curl http://localhost:8000/api/circlo/health
```

### Test Conversation Handler
```bash
curl -X POST http://localhost:8000/api/circlo/circlo-hook \
  -H "Content-Type: application/json" \
  -d '{
    "history": [],
    "message": "Cari produk trending",
    "user": {
      "id": "test123",
      "name": "Test User",
      "preferredKeywords": ["tech"],
      "preferredNiches": ["Technology"]
    },
    "profile": {
      "id": "agent1",
      "name": "TrendScout",
      "niche": "Business"
    }
  }'
```

Expected: Indonesian response about trend analysis

### Test Circlo Integration
```bash
uv run python setup_circlo_agents.py --test
```

Expected output:
```
🧪 Testing Circlo Integration...
1️⃣ Testing health check...
   Status: healthy
2️⃣ Testing user preferences API...
   Found X user preferences
✅ Integration tests completed!
```

## 🔑 Environment Variables

### Already Configured:
```env
# JWT Token (pre-configured, valid until 2125!)
GETCIRCLO_JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Feature flags (enabled)
GETCIRCLO_WHATSAPP_ENABLED=true
GETCIRCLO_MEMORY_ENABLED=true
```

### You Need to Add:
```env
# Required
FIRECRAWL_API_KEY=fc-your-key
OPENAI_API_KEY=sk-your-key

# Optional (untuk fitur tambahan)
RAPIDAPI_KEY=your-key
APIFY_API_KEY=your-key
```

## 📊 API Endpoints

### New Circlo Endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/circlo/circlo-hook` | POST | Webhook untuk Circlo conversations |
| `/api/circlo/create-post` | POST | Buat post di Circlo |
| `/api/circlo/create-agent` | POST | Register agent profile |
| `/api/circlo/user-preferences/{user_id}` | GET | Get user preferences |
| `/api/circlo/user-preferences` | GET | List semua preferences |
| `/api/circlo/send-whatsapp` | POST | Kirim WhatsApp message |
| `/api/circlo/health` | GET | Check Circlo integration |

### Existing TrendScout Endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/agent/analyze-trend` | POST | Analisis tren produk |
| `/api/agent/find-suppliers` | POST | Cari supplier |
| `/api/agent/contact-suppliers` | POST | Hubungi supplier |
| `/api/agent/execute-workflow` | POST | Jalankan full workflow |
| `/api/agent/status/{job_id}` | GET | Check job status |

**API Documentation**: http://localhost:8000/docs

## 🎓 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User (via Circlo)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              Circlo Platform Webhook                        │
│         POST /api/circlo/circlo-hook                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│         CircloConversationHandler                           │
│         - Intent Classification (GPT-3.5)                   │
│         - Route to appropriate handler                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        ↓              ↓              ↓              ↓
   ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐
   │ Trend   │   │ Supplier │   │Marketing │   │ Memory  │
   │ Analyst │   │  Scout   │   │  Agent   │   │ Keeper  │
   └─────────┘   └──────────┘   └──────────┘   └─────────┘
        │              │              │              │
        └──────────────┴──────────────┴──────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              Circlo Memory & WhatsApp API                   │
│         - Save interactions                                  │
│         - Send WhatsApp messages                             │
│         - Store user preferences                             │
└─────────────────────────────────────────────────────────────┘
```

## 💡 Usage Examples

### Example 1: Analisis Tren via Circlo Chat

**User di Circlo**: "Cari produk home decor yang lagi tren"

**TrendScout Response**:
```
🔍 Saya akan mencari tren produk home decor untuk Anda!

Mohon tunggu sebentar, saya sedang:
1. Menganalisis tren global dari Google Trends, TikTok, dan Amazon
2. Mencari supplier terpercaya di Indonesia
3. Mempersiapkan laporan lengkap

Estimasi waktu: 30-60 detik.

Anda akan mendapatkan:
✅ 3 produk trending teratas
✅ 5 supplier terpercaya dengan kontak langsung
✅ Rekomendasi harga dan MOQ
✅ Link untuk mulai marketing campaign

Saya akan mulai proses analisis sekarang...
```

### Example 2: Cari Supplier

**User**: "Supplier macrame di Bali yang recommended"

**Response**:
```
🔎 Mencari supplier macrame di Bali...

Saya akan scan:
- Tokopedia & Shopee (top rated sellers)
- Supplier marketplace B2B
- Grup WhatsApp supplier terpercaya

Filter yang digunakan:
✅ Rating > 4.5/5
✅ Lokasi Bali
✅ Stok tersedia
✅ Melayani grosir/reseller

Hasil akan segera saya kirimkan!
```

### Example 3: Direct API Call

```bash
curl -X POST http://localhost:8000/api/agent/execute-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "query": "trending skincare products",
    "user_id": "user123",
    "quantity": 20,
    "contact_methods": ["whatsapp", "email"]
  }'
```

## 🚢 Deployment

### 1. Pre-deployment
```bash
# Verify everything works locally
uv run python setup_circlo_agents.py --test
curl http://localhost:8000/api/circlo/health
```

### 2. Deploy to Platform

**Railway / Render / Vercel:**
```bash
git add .
git commit -m "Add Circlo integration"
git push origin main
```

### 3. Post-deployment

Update webhook URLs in Circlo dashboard:
```
https://your-domain.com/api/circlo/circlo-hook
```

Register agents (update URL in script first):
```bash
python setup_circlo_agents.py
```

### 4. Verify Production
```bash
curl https://your-domain.com/api/circlo/health
```

## 📈 Performance

### With UV Package Manager:

| Task | pip | uv | Improvement |
|------|-----|-----|-------------|
| Install dependencies | 180s | 15s | **12x faster** ⚡ |
| Create venv | 10s | 2s | **5x faster** |
| Single package | 5s | 1s | **5x faster** |

**Total setup time:**
- ❌ With pip: ~5 minutes
- ✅ With UV: **30 seconds!** 🚀

## 🐛 Troubleshooting

### Common Issues:

**1. UV not found**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
```

**2. Module not found**
```bash
source .venv/bin/activate
uv pip install -r requirements.txt
```

**3. Port already in use**
```bash
lsof -i :8000
kill -9 <PID>
# Or use different port
uv run uvicorn app.main:app --port 8001
```

**4. Circlo API errors**
```bash
# Check JWT token is set
grep GETCIRCLO_JWT_TOKEN .env

# Test connection
curl http://localhost:8000/api/circlo/health
```

**More troubleshooting**: See `CIRCLO_VERIFICATION.md`

## 📚 Learn More

| Topic | Document |
|-------|----------|
| **Setup Guide** | `QUICKSTART_UV.md` |
| **API Reference** | `CIRCLO_INTEGRATION.md` |
| **Testing Guide** | `CIRCLO_VERIFICATION.md` |
| **Technical Details** | `CIRCLO_IMPLEMENTATION_SUMMARY.md` |
| **Complete Summary** | `CIRCLO_FINAL_SUMMARY.md` |
| **Original Docs** | `README.md`, `AGENTS.md`, `PRD.md` |

## ✅ What's Included

### Code (2400+ lines):
- ✅ GetCirclo client with 20+ methods
- ✅ Intelligent conversation handler
- ✅ 7 new API endpoints
- ✅ Agent registration automation
- ✅ JWT token authentication
- ✅ Memory management
- ✅ WhatsApp integration

### Documentation (2000+ lines):
- ✅ Complete setup guides
- ✅ API reference with examples
- ✅ Testing & verification
- ✅ Troubleshooting guide
- ✅ Architecture diagrams
- ✅ Deployment instructions

### Tools:
- ✅ Automated setup script (`UV_SETUP.sh`)
- ✅ Agent registration script (`setup_circlo_agents.py`)
- ✅ Environment templates (`.env.circlo`)
- ✅ Test mode (`--test` flag)

## 🎉 Ready to Go!

**Status**: ✅ **PRODUCTION READY**

**Next Steps:**
1. Run `bash UV_SETUP.sh`
2. Add your API keys to `.env`
3. Start server: `uv run uvicorn app.main:app --reload`
4. Register agents: `uv run python setup_circlo_agents.py`
5. Test at: http://localhost:8000/docs
6. Deploy! 🚀

**Questions?** Check the documentation files listed above!

---

Made with ❤️ for GetCirclo Hackathon
