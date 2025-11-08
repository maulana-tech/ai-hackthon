# TrendScout - Quick Start with UV Package Manager

> **Super cepat setup dengan UV** - 10x lebih cepat dari pip!

## 🚀 Kenapa UV?

UV adalah package manager Python generasi baru yang:
- ⚡ **10-100x lebih cepat** dari pip
- 🔒 **Dependency resolution** yang lebih baik
- 📦 **Lockfile otomatis** untuk reproducibility
- 🎯 **Compatible** dengan pip & requirements.txt

## 📋 Prerequisites

- Python 3.9+
- macOS, Linux, atau Windows

## 1️⃣ Install UV

### macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Atau via pipx:
```bash
pipx install uv
```

### Verifikasi instalasi:
```bash
uv --version
# Output: uv 0.1.x atau lebih baru
```

## 2️⃣ Clone & Setup Project

```bash
# Clone repository
git clone <your-repo-url>
cd ai-hackthon

# Atau jika sudah di folder project
cd /Users/em/web/ai-hackthon
```

## 3️⃣ Create Virtual Environment dengan UV

```bash
# Buat venv dengan UV (sangat cepat!)
uv venv

# Activate venv
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

## 4️⃣ Install Dependencies dengan UV

```bash
# Install semua dependencies dari requirements.txt
# UV akan auto-detect dan install dengan sangat cepat!
uv pip install -r requirements.txt

# Atau install individual packages:
uv pip install fastapi uvicorn pydantic openai
```

**Kecepatan perbandingan:**
- ❌ `pip install -r requirements.txt` → 2-3 menit
- ✅ `uv pip install -r requirements.txt` → 10-20 detik! 🚀

## 5️⃣ Setup Environment Variables

### Copy template:
```bash
cp .env.example .env
```

### Edit `.env` file:
```env
# ===== MANDATORY API KEYS =====
FIRECRAWL_API_KEY=fc-YOUR-API-KEY
OPENAI_API_KEY=sk-YOUR-OPENAI-API-KEY

# GetCirclo Authentication (pilih salah satu)
GETCIRCLO_API_KEY=your-getcirclo-api-key
# ATAU gunakan JWT Token (recommended):
GETCIRCLO_JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEwZmRjNjkxLTIzMDAtNDM4Mi04ODI4LWE1NzI0YjQ5OTNiYiIsImVtYWlsIjoiZGV2QHNlbnRpLmdsb2JhbCIsImlzX2d1ZXN0IjpmYWxzZSwiaWF0IjoxNzYyNTcyMDYzLCJleHAiOjQ5MTgzMzIwNjN9.deShmmIRMKrRS1avZtNwY0u01_QwEcdBeDd_DJ2Qfxw

# GetCirclo Feature Flags
GETCIRCLO_WHATSAPP_ENABLED=true
GETCIRCLO_MEMORY_ENABLED=true

# ===== OPTIONAL API KEYS =====
RAPIDAPI_KEY=your-rapidapi-key
APIFY_API_KEY=your-apify-api-key

# Email Configuration (untuk outreach)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com

# Twilio WhatsApp (backup jika tidak pakai Circlo)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_WHATSAPP_NUMBER=+14155238886

# Database
DATABASE_URL=sqlite:///./data/trendscout.db
REDIS_URL=redis://localhost:6379/0
```

### GetCirclo Authentication Options:

**Option 1: JWT Token (Recommended)** ✅
```env
GETCIRCLO_JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Option 2: API Key**
```env
GETCIRCLO_API_KEY=your-getcirclo-api-key
```

System akan auto-detect dan prioritaskan JWT token jika tersedia.

## 6️⃣ Run Application dengan UV

### Option A: Menggunakan uvicorn langsung
```bash
# Development mode (auto-reload)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Option B: Run script langsung
```bash
uv run python app/main.py
```

### Option C: Run dengan bash script
```bash
chmod +x run.sh
./run.sh
```

**Server akan berjalan di:**
- 🌐 API Server: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- 📖 ReDoc: http://localhost:8000/redoc

## 7️⃣ Verify Installation

### Test imports:
```bash
uv run python -c "from app.main import app; print('✅ App loaded successfully')"
```

### Test health endpoints:
```bash
# Root endpoint
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health

# Circlo integration health
curl http://localhost:8000/api/circlo/health
```

## 8️⃣ Register Agents on Circlo

```bash
# Test Circlo connection
uv run python setup_circlo_agents.py --test

# Register all TrendScout agents
uv run python setup_circlo_agents.py
```

Expected output:
```
╔═══════════════════════════════════════════════════════════╗
║         TrendScout Circlo Agents Setup Script            ║
╚═══════════════════════════════════════════════════════════╝

🔍 Checking Circlo API connection...
✅ Circlo API is healthy
   WhatsApp enabled: true
   Memory enabled: true

📝 Registering 4 agents...
✅ Successfully registered: TrendScout Super Agent
✅ Successfully registered: TrendScout Analyst
✅ Successfully registered: TrendScout Supplier Connector
✅ Successfully registered: TrendScout Marketing Bot

✅ Successfully registered: 4/4
```

## 9️⃣ Test API Endpoints

### Test trend analysis:
```bash
curl -X POST http://localhost:8000/api/agent/analyze-trend \
  -H "Content-Type: application/json" \
  -d '{
    "query": "skincare products trending",
    "user_id": "user123",
    "region": "global"
  }'
```

### Test Circlo webhook:
```bash
curl -X POST http://localhost:8000/api/circlo/circlo-hook \
  -H "Content-Type: application/json" \
  -d '{
    "history": [],
    "message": "Cari produk skincare yang lagi tren",
    "user": {
      "id": "user123",
      "name": "Test User",
      "preferredKeywords": ["beauty"],
      "preferredNiches": ["Beauty"]
    },
    "profile": {
      "id": "agent1",
      "name": "TrendScout",
      "niche": "Business"
    }
  }'
```

## 🎯 UV Commands Cheat Sheet

### Package Management:
```bash
# Install package
uv pip install <package>

# Install from requirements.txt
uv pip install -r requirements.txt

# Install specific version
uv pip install fastapi==0.109.0

# Uninstall package
uv pip uninstall <package>

# List installed packages
uv pip list

# Show package info
uv pip show <package>

# Freeze dependencies
uv pip freeze > requirements.txt
```

### Environment Management:
```bash
# Create venv
uv venv

# Create with specific Python version
uv venv --python 3.11

# Remove venv
rm -rf .venv

# Activate venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Running Scripts:
```bash
# Run Python script
uv run python script.py

# Run with dependencies auto-install
uv run --with fastapi python script.py

# Run uvicorn
uv run uvicorn app.main:app --reload
```

## 🐛 Troubleshooting

### UV command not found
```bash
# Add UV to PATH
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Atau reinstall
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Dependencies not installing
```bash
# Clear UV cache
uv cache clean

# Reinstall dependencies
rm -rf .venv
uv venv
uv pip install -r requirements.txt
```

### Module not found errors
```bash
# Verify venv is activated
which python
# Should show: /path/to/project/.venv/bin/python

# If not activated:
source .venv/bin/activate

# Reinstall dependencies
uv pip install -r requirements.txt
```

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uv run uvicorn app.main:app --port 8001
```

## 🚀 Development Workflow

### Daily workflow:
```bash
# 1. Activate venv
source .venv/bin/activate

# 2. Update dependencies (if any)
uv pip install -r requirements.txt

# 3. Start development server
uv run uvicorn app.main:app --reload

# 4. Access API docs
open http://localhost:8000/docs
```

### Adding new dependencies:
```bash
# 1. Install with UV
uv pip install new-package

# 2. Update requirements.txt
uv pip freeze > requirements.txt

# 3. Commit changes
git add requirements.txt
git commit -m "Add new-package dependency"
```

### Running tests:
```bash
# Test specific file
uv run python test_agent.py

# Test indonetwork integration
uv run python test_indonetwork.py

# Test Circlo integration
uv run python setup_circlo_agents.py --test
```

## 📊 Performance Comparison

| Task | pip | uv | Speedup |
|------|-----|-----|---------|
| Install all dependencies | 180s | 15s | **12x faster** ⚡ |
| Create venv | 10s | 2s | **5x faster** |
| Install single package | 5s | 1s | **5x faster** |
| Dependency resolution | 30s | 3s | **10x faster** |

## 🎓 UV Best Practices

### 1. Always use virtual environments
```bash
# Good ✅
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Bad ❌
uv pip install -r requirements.txt  # Without venv
```

### 2. Use `uv run` for scripts
```bash
# Good ✅
uv run python script.py

# Good ✅ (with auto-install)
uv run --with requests python script.py

# Also good ✅
source .venv/bin/activate
python script.py
```

### 3. Keep requirements.txt updated
```bash
# After adding packages
uv pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
```

### 4. Use specific versions
```bash
# Good ✅
uv pip install fastapi==0.109.0

# Acceptable ✅
uv pip install fastapi

# Update requirements
uv pip freeze | grep fastapi >> requirements.txt
```

## 📚 Additional Resources

- UV Documentation: https://github.com/astral-sh/uv
- UV vs pip: https://astral.sh/blog/uv
- Python Packaging: https://packaging.python.org/

## ✅ Quick Verification Checklist

Run this to verify everything is working:

```bash
# 1. Check UV version
uv --version

# 2. Check Python in venv
source .venv/bin/activate
which python
python --version

# 3. Verify dependencies
uv pip list | grep -E "fastapi|openai|httpx"

# 4. Test imports
uv run python -c "from app.main import app; print('✅ All OK')"

# 5. Start server
uv run uvicorn app.main:app --reload

# 6. Test endpoint (in new terminal)
curl http://localhost:8000/health
```

Expected output at each step:
```
1. uv 0.1.x
2. /path/to/project/.venv/bin/python
   Python 3.9.x or higher
3. fastapi 0.109.0, openai 1.10.0, httpx 0.26.0
4. ✅ All OK
5. INFO: Uvicorn running on http://0.0.0.0:8000
6. {"status":"healthy"}
```

## 🎉 You're Ready!

Sekarang TrendScout sudah siap digunakan dengan UV package manager!

**Next steps:**
1. ✅ Configure `.env` dengan API keys Anda
2. ✅ Register agents: `uv run python setup_circlo_agents.py`
3. ✅ Test API endpoints di http://localhost:8000/docs
4. ✅ Update webhook URLs di Circlo dashboard
5. ✅ Start building amazing features! 🚀

**Support:**
- Issues: Check `CIRCLO_VERIFICATION.md`
- Documentation: See `CIRCLO_INTEGRATION.md`
- Questions: Review `QUICKSTART.md` & `README.md`
