# 🔧 Troubleshooting Guide - TrendScout

Panduan lengkap untuk mengatasi error yang sering terjadi saat instalasi dan menjalankan TrendScout.

## 📋 Table of Contents

1. [Masalah Instalasi Dependencies](#masalah-instalasi-dependencies)
2. [Masalah Python & Virtual Environment](#masalah-python--virtual-environment)
3. [Masalah API Keys](#masalah-api-keys)
4. [Masalah Saat Running Scripts](#masalah-saat-running-scripts)
5. [Masalah Database & Memory](#masalah-database--memory)
6. [Masalah Scraping & API](#masalah-scraping--api)

---

## 🚨 Masalah Instalasi Dependencies

### Error: `pip: command not found` atau `python: command not found`

**Penyebab:** Python atau pip tidak terinstall atau tidak ada di PATH

**Solusi:**

```bash
# Check Python version
python3 --version
# Atau
python --version

# Jika tidak ada, install Python terlebih dahulu

# macOS (menggunakan Homebrew)
brew install python@3.9

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.9 python3-pip

# Windows
# Download dari https://www.python.org/downloads/
```

### Error: `ModuleNotFoundError: No module named 'firecrawl'`

**Penyebab:** Dependencies belum terinstall atau virtual environment tidak aktif

**Solusi:**

```bash
# Pastikan virtual environment aktif
source .venv/bin/activate  # macOS/Linux
# atau
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Atau menggunakan uv (lebih cepat)
uv pip install -e .

# Untuk specific package
pip install firecrawl-py
```

### Error: `uv: command not found`

**Penyebab:** UV package manager belum terinstall

**Solusi:**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload shell
source ~/.bashrc  # atau ~/.zshrc

# Verify
uv --version

# Alternatif: install via pip
pip install uv
```

### Error: `ERROR: Could not build wheels for XXX`

**Penyebab:** Missing build tools atau compiler

**Solusi:**

```bash
# macOS
xcode-select --install

# Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# Fedora/RHEL
sudo dnf install gcc python3-devel

# Windows
# Install Visual C++ Build Tools
# https://visualstudio.microsoft.com/downloads/
```

### Error: `SSL: CERTIFICATE_VERIFY_FAILED`

**Penyebab:** SSL certificate tidak valid (sering di corporate network)

**Solusi:**

```bash
# Temporary fix (NOT RECOMMENDED for production)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package>

# Better: Install certificates
# macOS
/Applications/Python\ 3.9/Install\ Certificates.command

# Ubuntu
sudo apt-get install ca-certificates
sudo update-ca-certificates
```

### Error: `pip install` sangat lambat

**Penyebab:** Network issue atau pypi.org lambat

**Solusi:**

```bash
# Gunakan UV (10-100x lebih cepat)
pip install uv
uv pip install -r requirements.txt

# Atau gunakan mirror (untuk Indonesia)
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <package>
```

---

## 🐍 Masalah Python & Virtual Environment

### Error: `ImportError: cannot import name 'XXX'`

**Penyebab:** Dependencies tidak compatible atau salah versi Python

**Solusi:**

```bash
# Check Python version (harus 3.8+)
python --version

# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Error: `ModuleNotFoundError` walaupun sudah install

**Penyebab:** Menggunakan Python system bukan virtual environment

**Solusi:**

```bash
# Pastikan venv aktif
which python
# Harus menunjuk ke: /path/to/project/.venv/bin/python

# Jika tidak, activate venv
source .venv/bin/activate

# Verify
python -c "import sys; print(sys.prefix)"
# Harus menunjuk ke .venv
```

### Error: `SyntaxError: invalid syntax` (f-string, walrus operator, dll)

**Penyebab:** Python version terlalu lama

**Solusi:**

```bash
# Check version
python --version

# TrendScout memerlukan Python 3.8+
# Upgrade Python atau gunakan versi yang benar

# Create venv dengan specific Python version
python3.9 -m venv .venv
source .venv/bin/activate
```

### Virtual Environment tidak activate otomatis

**Solusi:**

```bash
# Tambahkan ke shell profile (~/.bashrc atau ~/.zshrc)
# Auto-activate venv saat cd ke project
cd() {
  builtin cd "$@"
  if [[ -d ".venv" ]]; then
    source .venv/bin/activate
  fi
}
```

---

## 🔑 Masalah API Keys

### Error: `FIRECRAWL_API_KEY not found`

**Penyebab:** `.env` file tidak ada atau tidak ter-load

**Solusi:**

```bash
# 1. Copy template
cp .env.example .env

# 2. Edit .env dan isi API keys
nano .env  # atau gunakan text editor lain

# 3. Verify .env file loaded
python -c "from app.config import get_settings; print(get_settings().firecrawl_api_key)"

# 4. Jika masih error, explicitly load .env
pip install python-dotenv

# Di code Python:
from dotenv import load_dotenv
load_dotenv()
```

### Error: `Invalid API key` atau `401 Unauthorized`

**Penyebab:** API key salah atau expired

**Solusi:**

```bash
# 1. Verify API key format
echo $FIRECRAWL_API_KEY
# Harus dimulai dengan "fc-"

# 2. Get new API key
# Firecrawl: https://www.firecrawl.dev/app/api-keys
# OpenAI: https://platform.openai.com/api-keys

# 3. Check API key valid
curl -H "Authorization: Bearer fc-YOUR-KEY" \
  https://api.firecrawl.dev/v1/scrape

# 4. Update .env
nano .env
# FIRECRAWL_API_KEY=fc-new-key-here
```

### Error: `.env` file ada tapi tidak ter-load

**Penyebab:** File location salah atau permission issue

**Solusi:**

```bash
# 1. Pastikan .env di root project
ls -la .env
# Output: -rw-r--r--  1 user  staff  1234 Nov  8 20:00 .env

# 2. Check file permissions
chmod 644 .env

# 3. Verify content
cat .env | grep FIRECRAWL_API_KEY

# 4. Explicitly load in Python
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
```

---

## 🏃 Masalah Saat Running Scripts

### Error: `python: can't open file 'app/main.py': No such file or directory`

**Penyebab:** Running command dari directory yang salah

**Solusi:**

```bash
# 1. Check current directory
pwd
# Harus di root project: /path/to/ai-hackthon

# 2. Change ke root project
cd /path/to/ai-hackthon

# 3. Verify file exists
ls app/main.py

# 4. Run with absolute path
python /full/path/to/ai-hackthon/app/main.py

# 5. Atau gunakan python -m
python -m app.main
```

### Error: `ModuleNotFoundError: No module named 'app'`

**Penyebab:** Python tidak menemukan module path

**Solusi:**

```bash
# Method 1: Install as editable package
pip install -e .

# Method 2: Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python app/main.py

# Method 3: Add to script
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Method 4: Gunakan python -m
python -m app.main
```

### Error: `Address already in use` (port 8000)

**Penyebab:** Port sudah digunakan oleh process lain

**Solusi:**

```bash
# 1. Find process using port 8000
# macOS/Linux
lsof -i :8000
# atau
netstat -tulpn | grep 8000

# 2. Kill process
kill -9 <PID>

# 3. Atau gunakan port lain
uvicorn app.main:app --port 8001

# 4. Atau stop semua Python processes
pkill -9 python
```

### Error: `tests/test_xxx.py` timeout atau hang

**Penyebab:** Scraping terlalu lama atau API rate limit

**Solusi:**

```bash
# 1. Increase timeout
# Di test file, ubah:
@pytest.mark.asyncio
async def test_something():
    await asyncio.wait_for(some_function(), timeout=120)

# 2. Skip slow tests
pytest -m "not slow"

# 3. Run specific test
pytest tests/test_bestseller_finder.py::test_intent_classification

# 4. Mock API calls untuk testing
# Gunakan pytest-mock atau unittest.mock
```

### Error: `RuntimeError: Event loop is closed`

**Penyebab:** Asyncio event loop issues

**Solusi:**

```python
# Tambahkan di awal script
import asyncio
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Atau gunakan:
if __name__ == "__main__":
    asyncio.run(main())
```

---

## 💾 Masalah Database & Memory

### Error: `PermissionError: [Errno 13] Permission denied: 'data/memory'`

**Penyebab:** Directory permission

**Solusi:**

```bash
# Create directories dengan permission yang benar
mkdir -p data/memory logs

# Fix permissions
chmod -R 755 data logs

# Atau jalankan dengan sudo (NOT RECOMMENDED)
sudo python app/main.py
```

### Error: `JSONDecodeError: Expecting value`

**Penyebab:** Corrupt JSON file di memory storage

**Solusi:**

```bash
# 1. Backup existing data
cp -r data/memory data/memory.backup

# 2. Clear corrupt files
rm -rf data/memory/*.json

# 3. Restart app (akan create new files)
python app/main.py

# 4. Atau manually fix JSON
# Validate JSON:
python -m json.tool data/memory/user_123.json
```

---

## 🌐 Masalah Scraping & API

### Error: `Firecrawl API returned status 404` atau `402`

**Penyebab:** 
- 404: URL tidak ditemukan
- 402: Firecrawl credit habis atau API key invalid

**Solusi:**

```bash
# 1. Check Firecrawl credit
# Login ke https://www.firecrawl.dev/app

# 2. Verify URL accessible
curl -I https://www.tokopedia.com

# 3. Test Firecrawl API directly
curl -X POST https://api.firecrawl.dev/v1/scrape \
  -H "Authorization: Bearer fc-YOUR-KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tokopedia.com"}'

# 4. Use fallback scraping
# Edit config.py:
USE_APIFY = True  # Gunakan Apify jika Firecrawl gagal
```

### Error: `ConnectionError` atau `TimeoutError`

**Penyebab:** Network issue atau API down

**Solusi:**

```python
# 1. Increase timeout
import httpx

async with httpx.AsyncClient(timeout=60.0) as client:
    response = await client.get(url)

# 2. Add retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def scrape_with_retry(url):
    return await firecrawl.scrape(url)

# 3. Check internet connection
ping google.com

# 4. Check if API is down
# https://status.firecrawl.dev
```

### Error: `Rate limit exceeded`

**Penyebab:** Terlalu banyak request ke API

**Solusi:**

```python
# 1. Add rate limiting
import asyncio
from asyncio import Semaphore

semaphore = Semaphore(5)  # Max 5 concurrent requests

async def scrape_with_limit(url):
    async with semaphore:
        await asyncio.sleep(0.5)  # 500ms delay
        return await firecrawl.scrape(url)

# 2. Implement caching
from functools import lru_cache
import time

cache = {}

async def cached_scrape(url, ttl=3600):
    if url in cache:
        timestamp, data = cache[url]
        if time.time() - timestamp < ttl:
            return data
    
    data = await firecrawl.scrape(url)
    cache[url] = (time.time(), data)
    return data
```

### Error: `Expecting value: line 1 column 1 (char 0)` saat parsing JSON

**Penyebab:** Response bukan JSON atau kosong

**Solusi:**

```python
# 1. Add error handling
try:
    result = json.loads(response)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON: {response[:200]}")
    result = {}

# 2. Validate response before parsing
if response and isinstance(response, str):
    result = json.loads(response)
else:
    result = {}

# 3. Use safe JSON parsing
import json
from typing import Any, Dict

def safe_json_loads(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {}
```

---

## 🔍 Debug Mode

Enable debug mode untuk troubleshooting:

```bash
# Set environment variable
export DEBUG=1
export LOG_LEVEL=DEBUG

# Run with debug
python app/main.py

# Check logs
tail -f logs/app.log
```

Debug script untuk test individual components:

```python
# tests/debug_component.py
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)

async def debug_test():
    from app.agents.bestseller_finder import BestsellerFinder
    
    finder = BestsellerFinder()
    
    try:
        result = await finder.find_bestsellers(
            category="fashion",
            limit=3
        )
        
        print(f"✅ Success: Found {len(result)} products")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_test())
```

---

## 📞 Getting Help

Jika masih mengalami error:

1. **Check Logs**: `cat logs/app.log | tail -100`
2. **Enable Debug**: Set `LOG_LEVEL=DEBUG` in `.env`
3. **Run Tests**: `pytest -v tests/`
4. **Check GitHub Issues**: [Project Issues](https://github.com/your-repo/issues)
5. **Contact Support**: support@trendscout.ai

---

## 📚 Useful Commands Cheat Sheet

```bash
# === Virtual Environment ===
python3 -m venv .venv
source .venv/bin/activate
deactivate

# === Dependencies ===
pip install -r requirements.txt
pip list
pip freeze > requirements.txt

# === UV (Fast Package Manager) ===
uv pip install -e .
uv run python app/main.py
uv pip list

# === Running ===
python app/main.py
uvicorn app.main:app --reload
python -m app.main

# === Testing ===
pytest
pytest -v tests/
pytest tests/test_specific.py::test_function
pytest -k "bestseller"

# === Debugging ===
python -m pdb app/main.py
import pdb; pdb.set_trace()

# === Logs ===
tail -f logs/app.log
grep "ERROR" logs/app.log

# === Cleanup ===
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
rm -rf .pytest_cache
```

---

**Last Updated:** 2025-11-08  
**Version:** 2.0.0
