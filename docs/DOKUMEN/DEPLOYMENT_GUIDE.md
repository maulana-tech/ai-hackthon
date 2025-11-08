# 🚀 TrendScout AI - GetCirclo Deployment Guide

Complete guide for deploying TrendScout AI Agent to GetCirclo platform.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Local Testing](#local-testing)
4. [Production Deployment](#production-deployment)
5. [Agent Registration](#agent-registration)
6. [Testing & Verification](#testing--verification)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

### Required Accounts & Credentials

- [x] **GetCirclo Account** - Contact admin for JWT token
- [x] **Firecrawl API Key** - For web scraping
- [x] **OpenRouter API Key** - For LLM (or OpenAI)
- [x] **Production Server** - To host the agent (VPS, Cloud, etc)

### System Requirements

```
Python: 3.9+
RAM: 2GB minimum, 4GB recommended
Storage: 5GB minimum
Bandwidth: Unlimited or generous limits
```

---

## 🔧 Environment Setup

### 1. Environment Variables

Create or update `.env` file with production values:

```bash
# Application
APP_NAME="TrendScout Supplier Connector"
APP_VERSION="1.0.0"
DEBUG=false
LOG_LEVEL="INFO"

# GetCirclo Integration (REQUIRED)
GETCIRCLO_API_KEY=your_getcirclo_api_key_here
GETCIRCLO_JWT_TOKEN=your_jwt_token_here
GETCIRCLO_WHATSAPP_ENABLED=true
GETCIRCLO_MEMORY_ENABLED=true

# Agent Webhook (REQUIRED for GetCirclo)
AGENT_WEBHOOK_URL=https://your-production-domain.com/circlo-webhook/hook

# Firecrawl (REQUIRED)
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# LLM Provider (Choose one)
# Option 1: OpenRouter (Recommended)
OPENROUTER_API_KEY=your_openrouter_key_here
LLM_PROVIDER=openrouter
LLM_MODEL=qwen/qwen-2.5-coder-32b-instruct

# Option 2: OpenAI
# OPENAI_API_KEY=your_openai_key_here
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4

# Apify (Optional - for marketplace scraping)
APIFY_API_KEY=your_apify_key_here

# Email (Optional - for supplier outreach)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com

# WhatsApp (Optional - via Twilio)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_WHATSAPP_NUMBER=+14155238886

# Database & Cache
DATABASE_URL=sqlite:///./data/trendscout.db
REDIS_URL=redis://localhost:6379/0

# Performance
MAX_RETRIES=3
TIMEOUT_SECONDS=120
SCRAPING_SPEED=10
CACHE_TTL_HOURS=24
```

### 2. Get Your JWT Token

**Contact GetCirclo Admin**:
- Email: admin@getcirclo.com
- Or use development endpoint: https://api.getcirclo.com

**For Testing**:
```bash
curl -X GET \
  "https://api.getcirclo.com/api/user-preferences" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

If you get user preferences, your token is valid! ✅

---

## 🧪 Local Testing

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Start Local Server

```bash
# Method 1: Direct run
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Method 2: Using script
chmod +x run.sh
./run.sh
```

### 3. Verify Server is Running

```bash
# Health check
curl http://localhost:8000/health

# API info
curl http://localhost:8000/

# Webhook info
curl http://localhost:8000/circlo-webhook/webhook-info
```

### 4. Test with ngrok (For Local Testing)

```bash
# Install ngrok
brew install ngrok  # Mac
# or download from https://ngrok.com

# Start tunnel
ngrok http 8000

# Copy HTTPS URL
# Example: https://abc123.ngrok.io

# Set webhook URL
export AGENT_WEBHOOK_URL=https://abc123.ngrok.io/circlo-webhook/hook
```

### 5. Test Webhook Locally

```bash
curl -X POST http://localhost:8000/circlo-webhook/hook \
  -H "Content-Type: application/json" \
  -d '{
    "history": [],
    "message": "Carikan produk elektronik terlaris",
    "user": {
      "id": "test-123",
      "name": "Test User",
      "preferredKeywords": ["elektronik"],
      "preferredNiches": ["Tech"]
    },
    "profile": {
      "id": "agent-123",
      "name": "TrendScout AI",
      "niche": "E-commerce"
    }
  }'
```

**Expected Response**:
```json
{
  "response": "🔥 Hai Test User! Saya menemukan 5 produk terlaris untuk Anda:..."
}
```

---

## 🌐 Production Deployment

### Option 1: VPS (DigitalOcean, AWS, GCP)

#### 1.1 Setup Server

```bash
# SSH into server
ssh user@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip python3-venv -y

# Install nginx (for reverse proxy)
sudo apt install nginx -y
```

#### 1.2 Clone Repository

```bash
# Clone your repo
git clone https://github.com/your-username/ai-hackthon.git
cd ai-hackthon

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 1.3 Setup Environment

```bash
# Copy environment file
cp .env.example .env

# Edit with your credentials
nano .env

# Create directories
mkdir -p data logs data/cache
```

#### 1.4 Setup Systemd Service

Create `/etc/systemd/system/trendscout.service`:

```ini
[Unit]
Description=TrendScout AI Agent
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/ai-hackthon
Environment="PATH=/home/your-username/ai-hackthon/.venv/bin"
ExecStart=/home/your-username/ai-hackthon/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable trendscout
sudo systemctl start trendscout

# Check status
sudo systemctl status trendscout
```

#### 1.5 Setup Nginx Reverse Proxy

Create `/etc/nginx/sites-available/trendscout`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /circlo-webhook {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 30s;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/trendscout /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 1.6 Setup SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is setup automatically
```

### Option 2: Docker Deployment

```bash
# Build image
docker build -t trendscout-ai .

# Run container
docker run -d \
  --name trendscout \
  --restart always \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  trendscout-ai

# Check logs
docker logs -f trendscout
```

### Option 3: Heroku Deployment

```bash
# Login to Heroku
heroku login

# Create app
heroku create trendscout-ai

# Set config vars
heroku config:set GETCIRCLO_JWT_TOKEN=your_token
heroku config:set FIRECRAWL_API_KEY=your_key
heroku config:set OPENROUTER_API_KEY=your_key
# ... set all other env vars

# Deploy
git push heroku main

# Open app
heroku open
```

---

## 🤖 Agent Registration

### 1. Set Webhook URL

```bash
# For production
export AGENT_WEBHOOK_URL=https://your-domain.com/circlo-webhook/hook

# For ngrok (local testing)
export AGENT_WEBHOOK_URL=https://abc123.ngrok.io/circlo-webhook/hook
```

### 2. Run Registration Script

```bash
# Activate virtual environment
source .venv/bin/activate

# Run registration
python scripts/register_circlo_agent.py
```

### 3. Verify Registration

The script will output:

```
✅ AGENT REGISTERED SUCCESSFULLY!
════════════════════════════════════════
Agent ID: 550e8400-e29b-41d4-a716-446655440000
Name: TrendScout AI
Username: trendscout-ai
Niche: E-commerce & Business
Endpoint: https://your-domain.com/circlo-webhook/hook
Is Agent: true
Created At: 2025-11-08T12:00:00Z
```

---

## ✅ Testing & Verification

### 1. Test via GetCirclo Platform

**Start a conversation** with your agent:
- Open GetCirclo app
- Search for `@trendscout-ai`
- Start chatting!

**Sample Test Queries**:

```
User: Hai! Carikan produk elektronik yang lagi trending

Expected: Agent responds with trending electronics products

---

User: Tolong carikan 5 produk fashion terlaris

Expected: Agent finds bestselling fashion products

---

User: Cari supplier tas di Jakarta dengan rating tinggi

Expected: Agent finds suppliers with contact info
```

### 2. Monitor Logs

```bash
# Tail logs
tail -f logs/server.log

# Or with systemd
sudo journalctl -u trendscout -f

# Or with Docker
docker logs -f trendscout
```

### 3. Check Webhook Requests

Look for logs like:

```
[GetCirclo Webhook] Received message from user: John Doe (ID: xxx)
[GetCirclo Webhook] Message: Carikan produk elektronik terlaris
[GetCirclo Webhook] Processing query through SuperAgent...
[GetCirclo Webhook] SuperAgent result status: completed
[GetCirclo Webhook] Detected intent: find_bestsellers
[GetCirclo Webhook] Generated response length: 450 chars
```

---

## 📊 Monitoring

### Key Metrics to Monitor

1. **Response Time** - Should be < 30 seconds
2. **Success Rate** - Should be > 95%
3. **Cache Hit Rate** - Should be > 80% after warmup
4. **API Errors** - Should be minimal

### Setup Monitoring (Optional)

#### Sentry for Error Tracking

```bash
pip install sentry-sdk
```

Add to `app/main.py`:

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

#### Simple Health Check Script

Create `scripts/health_check.sh`:

```bash
#!/bin/bash
RESPONSE=$(curl -s http://localhost:8000/health)
if [ "$RESPONSE" == '{"status":"healthy"}' ]; then
    echo "✅ Service is healthy"
    exit 0
else
    echo "❌ Service is unhealthy"
    exit 1
fi
```

Add to crontab:

```bash
*/5 * * * * /path/to/health_check.sh >> /var/log/trendscout-health.log 2>&1
```

---

## 🐛 Troubleshooting

### Issue 1: Webhook Returns 500 Error

**Symptoms**:
- GetCirclo shows error
- Logs show exception

**Solutions**:
1. Check logs for specific error
2. Verify all environment variables are set
3. Test locally with curl
4. Check API rate limits

### Issue 2: Agent Not Responding

**Symptoms**:
- User sends message but no response
- Webhook not being called

**Solutions**:
1. Verify agent registration was successful
2. Check webhook URL is accessible from internet
3. Test webhook with curl from external source
4. Check firewall/security group settings

### Issue 3: Slow Responses

**Symptoms**:
- Responses take > 30 seconds
- GetCirclo timeout errors

**Solutions**:
1. Enable caching (already implemented)
2. Optimize database queries
3. Use Redis instead of file cache
4. Increase server resources

### Issue 4: Rate Limiting

**Symptoms**:
- Empty results
- API errors in logs

**Solutions**:
- Already fixed! (see FIXES_COMPLETED.md)
- Caching prevents most rate limit issues
- Fallback data ensures always-working system

### Debug Mode

Enable debug logging:

```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG

# Restart service
sudo systemctl restart trendscout
```

---

## 📝 Production Checklist

Before going live, verify:

- [ ] All environment variables are set
- [ ] JWT token is valid and not expired
- [ ] Webhook URL is accessible from internet
- [ ] HTTPS is enabled (SSL certificate)
- [ ] Server has adequate resources (2GB+ RAM)
- [ ] Logs directory is writable
- [ ] Data directory is writable
- [ ] Service auto-starts on boot
- [ ] Health check endpoint works
- [ ] Agent is registered on GetCirclo
- [ ] Test conversation works end-to-end
- [ ] Monitoring is setup (optional but recommended)
- [ ] Backups are configured (optional)

---

## 🎉 Success!

Once deployed, your agent will be available 24/7 on GetCirclo platform!

Users can interact with `@trendscout-ai` to:
- Find trending products
- Discover bestsellers
- Get supplier recommendations
- Receive WhatsApp contact info
- Get actionable business insights

---

## 📚 Additional Resources

- **GetCirclo API Docs**: `docs/CIRCLO.md`
- **Fixes Documentation**: `FIXES_COMPLETED.md`
- **Quick Start**: `QUICKSTART.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`

---

**Need Help?**

- Check logs first: `tail -f logs/server.log`
- Review error messages carefully
- Test components individually
- Contact GetCirclo support if needed

**🚀 Happy Deploying!**
