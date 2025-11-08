# 🚇 Ngrok + GetCirclo Setup Guide - Complete Integration

## Overview

Setup TrendScout AI Agent dengan GetCirclo menggunakan Ngrok untuk testing.

**Sistem yang Sudah Ada:**
- ✅ Beautiful HTML campaign websites
- ✅ 5 automated next steps (Gemini + Qwen)
- ✅ GetCirclo webhook integration (`/circlo-webhook/hook`)
- ✅ Mobile-optimized responsive design

---

## Quick Start (5 Minutes)

### Step 1: Install & Configure Ngrok

```bash
# Install ngrok
brew install ngrok

# Sign up & get auth token: https://ngrok.com/signup
# Configure auth token (one-time)
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### Step 2: Start Services

```bash
cd /Users/em/web/ai-hackthon

# Start server + ngrok (all-in-one)
./start_ngrok.sh
```

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    🎉 SETUP COMPLETE!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 URLS:
  🌐 Ngrok Public URL: https://abc123.ngrok.io
  📊 Ngrok Dashboard:  http://127.0.0.1:4040
  🔗 GetCirclo Webhook: https://abc123.ngrok.io/circlo-webhook/hook

📝 NEXT STEPS:
1️⃣  Register Agent on GetCirclo (One-time)
2️⃣  Test in GetCirclo App
3️⃣  Monitor Activity
```

### Step 3: Register Agent on GetCirclo

```bash
# Register agent (one-time only)
python3 scripts/register_circlo_agent.py
```

**Output:**
```
🤖 REGISTERING TRENDSCOUT AI AGENT ON GETCIRCLO
════════════════════════════════════════════════

Agent Name: TrendScout AI
Username: trendscout-ai
Niche: E-commerce & Business
Webhook URL: https://abc123.ngrok.io/circlo-webhook/hook

✅ JWT Token found
📡 Sending registration request...
✅ Agent registered successfully!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGENT PROFILE CREATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🆔 ID: abc-123-def-456
📝 Name: TrendScout AI
👤 Username: @trendscout-ai
🏷️ Niche: E-commerce & Business
🔗 Webhook: https://abc123.ngrok.io/circlo-webhook/hook
```

### Step 4: Test in GetCirclo App

1. Open GetCirclo app
2. Search: `@trendscout-ai`
3. Start conversation
4. Send test message:

```
Buat kampanye marketing untuk smartwatch
```

**Expected Response:**
```
🎯 Hai [Your Name]! Kampanye untuk smartwatch sudah siap!

💰 Budget: Rp 5.000.000
📅 Durasi: 30 hari

🤖 Next Steps Auto-Executed!

✅ Review: Campaign readiness score 8/10
✅ Budget: Optimized untuk Instagram, TikTok
✅ Content Calendar: 30 posts generated
✅ Tracking: Google Sheets ready
✅ Launch Checklist: 12 tasks ready

🚀 Campaign ready untuk launch!

📄 Campaign Document:
https://abc123.ngrok.io/documents/408da2a54639/view

💡 Klik untuk view complete campaign plan
```

### Step 5: View Beautiful Campaign Website

Click document URL → Opens professional HTML website dengan:

- 📊 **Stats Dashboard**: Duration, Platforms, KPIs
- 🚀 **Platform Strategy**: Instagram, Facebook, TikTok, Tokopedia cards
- 📈 **KPI List**: Reach, engagement, CTR metrics
- 💡 **Recommendations**: Best practices list
- 📥 **Download Button**: Get markdown file
- 📊 **Tracking Sheet**: Create Google Sheets

---

## Architecture

```
User Message → GetCirclo Platform → Ngrok Tunnel → FastAPI Server
                                                          ↓
                                              SuperAgent Processing
                                                          ↓
                        Campaign Generation + Document Creation
                                                          ↓
                            5 Automated Steps (Parallel)
                                                          ↓
                      1. Review & Validation (Gemini)
                      2. Budget Optimization (Qwen)
                      3. Content Calendar (Gemini)
                      4. Tracking Setup (Both)
                      5. Launch Checklist (Gemini)
                                                          ↓
                     Beautiful HTML Website + Response
                                                          ↓
                              Return to GetCirclo → User
```

---

## What Each Component Does

### 1. Ngrok Tunnel
- Exposes local server (port 8000) to internet
- Provides HTTPS URL for GetCirclo webhook
- Free tier: URL changes on restart

### 2. GetCirclo Webhook (`/circlo-webhook/hook`)
- Receives user messages from GetCirclo
- Payload includes: message, history, user preferences, profile
- Expected response: `{"response": "text"}` (within 30 seconds)

### 3. Document Service
- Generates beautiful HTML campaign websites
- Stores with unique doc_id
- Returns shareable URL: `https://ngrok-url/documents/{doc_id}/view`

### 4. Campaign Automation
- Executes 5 next steps automatically (parallel)
- Uses Gemini (fast) + Qwen (complex reasoning)
- Total time: ~15 seconds

---

## Monitoring & Debugging

### View Logs

```bash
# Watch server logs
tail -f logs/server.log

# Look for:
# [GetCirclo Webhook] Received message from user: John
# [GetCirclo Webhook] Intent: marketing_campaign
# 🤖 Starting automated next steps...
# ✅ Campaign + Automation completed
```

### View Ngrok Traffic

```bash
# Open ngrok dashboard
open http://127.0.0.1:4040

# Or in browser: http://127.0.0.1:4040
```

Shows all HTTP requests/responses to your webhook.

### Test Webhook Locally

```bash
# Test webhook endpoint
curl -X POST http://localhost:8000/circlo-webhook/hook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "test",
    "user": {"id": "1", "name": "Test", "preferredKeywords": [], "preferredNiches": []},
    "profile": {"id": "1", "name": "Agent", "niche": "Test"},
    "history": []
  }'
```

### Check Document Generation

```bash
# Generate test campaign
curl -X POST https://YOUR-NGROK-URL.ngrok.io/circlo-webhook/hook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Buat kampanye untuk fashion",
    "user": {"id": "test", "name": "Test", "preferredKeywords": [], "preferredNiches": []},
    "profile": {"id": "1", "name": "TrendScout AI", "niche": "Ecommerce"},
    "history": []
  }'

# View document (get URL from response)
open https://YOUR-NGROK-URL.ngrok.io/documents/DOC-ID/view
```

---

## Commands Reference

### Start Services
```bash
./start_ngrok.sh
```

### Stop Services
```bash
./stop_services.sh
# Or: Ctrl+C in terminal
```

### Register Agent
```bash
python3 scripts/register_circlo_agent.py
```

### Test GetCirclo Connection
```bash
python3 scripts/test_getcirclo_connection.py
```

### View Logs
```bash
tail -f logs/server.log
```

---

## Environment Variables

Required in `.env`:

```bash
# GetCirclo
GETCIRCLO_API_KEY=your_api_key
GETCIRCLO_JWT_TOKEN=your_jwt_token
GETCIRCLO_WHATSAPP_ENABLED=true
GETCIRCLO_MEMORY_ENABLED=true

# LLMs (for automation)
GEMINI_API_KEY=your_gemini_key
OPENROUTER_API_KEY=your_openrouter_key

# Set by script automatically
APP_BASE_URL=https://abc123.ngrok.io
AGENT_WEBHOOK_URL=https://abc123.ngrok.io/circlo-webhook/hook
```

---

## Troubleshooting

### Issue: Agent registration fails

**Symptoms**: Script returns error during registration

**Solutions**:
```bash
# 1. Check JWT token
grep GETCIRCLO_JWT_TOKEN .env

# 2. Test connection
python3 scripts/test_getcirclo_connection.py

# 3. Check webhook URL
echo $AGENT_WEBHOOK_URL
# Should be: https://YOUR-NGROK-URL.ngrok.io/circlo-webhook/hook
```

### Issue: Document URL returns 404

**Cause**: Server not using ngrok URL for document generation

**Solution**:
```bash
# Stop and restart with correct URL
./stop_services.sh
./start_ngrok.sh

# APP_BASE_URL will be set automatically
```

### Issue: GetCirclo not receiving responses

**Cause**: Webhook timeout (>30s) or server error

**Solutions**:
```bash
# 1. Check server is running
curl http://localhost:8000/health

# 2. Check logs
tail -f logs/server.log

# 3. Test webhook locally
curl -X POST http://localhost:8000/circlo-webhook/hook \
  -H "Content-Type: application/json" \
  -d '{"message":"test","user":{"id":"1","name":"Test","preferredKeywords":[],"preferredNiches":[]},"profile":{"id":"1","name":"Agent","niche":"Test"},"history":[]}'
```

### Issue: Ngrok URL changed after restart

**Cause**: Free tier generates new URL each restart

**Solution**:
```bash
# 1. Restart services (gets new URL)
./start_ngrok.sh

# 2. Re-register agent with new URL
python3 scripts/register_circlo_agent.py

# Alternative: Upgrade to Ngrok Pro for fixed domain
```

### Issue: Automation not executing

**Symptoms**: Campaign generated but no automation results

**Solutions**:
```bash
# 1. Check LLM API keys
grep GEMINI_API_KEY .env
grep OPENROUTER_API_KEY .env

# 2. Check logs for errors
grep "automation" logs/server.log

# 3. Test locally
curl -X POST http://localhost:8000/circlo-webhook/hook \
  -H "Content-Type: application/json" \
  -d '{"message":"Buat kampanye untuk test","user":{"id":"1","name":"Test","preferredKeywords":[],"preferredNiches":[]},"profile":{"id":"1","name":"Agent","niche":"Test"},"history":[]}'
```

---

## Ngrok Limitations (Free Tier)

### What's Included:
- ✅ 1 online process
- ✅ HTTPS tunnels
- ✅ 40 connections/minute
- ❌ URL changes on restart
- ❌ 2-hour session timeout

### Upgrade to Pro ($10/month):
- ✅ Fixed custom domain
- ✅ No session timeout
- ✅ More connections
- ✅ Reserved subdomain

```bash
# With Pro, use fixed domain:
ngrok http 8000 --domain=your-app.ngrok.io
```

---

## Production Deployment

For production (permanent setup), see:
- `DEPLOYMENT_GUIDE.md` - Full VPS deployment
- `QUICK_DEPLOY.md` - Quick deployment options
- `AUTO_CAMPAIGN_GENERATION.md` - System architecture

---

## Success Checklist

Before using with GetCirclo:

- [ ] Ngrok installed and authenticated
- [ ] Server running on port 8000
- [ ] Ngrok tunnel active (check dashboard)
- [ ] `APP_BASE_URL` set to ngrok URL
- [ ] `AGENT_WEBHOOK_URL` set correctly
- [ ] Agent registered on GetCirclo
- [ ] Can find `@trendscout-ai` in GetCirclo
- [ ] Test message returns response
- [ ] Document URL opens correctly
- [ ] Beautiful HTML website displays
- [ ] Automation results show in response

---

## What Users Get

When they send "Buat kampanye untuk [product]":

1. **Instant Response** (~20 seconds total)
2. **Formatted Message** with campaign summary
3. **Automation Summary**:
   - ✅ Review: Readiness score 8/10
   - ✅ Budget: Optimized for top platforms
   - ✅ Calendar: 30 posts generated
   - ✅ Tracking: Sheets ready
   - ✅ Checklist: Tasks ready
4. **Beautiful Website URL** (clickable)
5. **Professional Design**:
   - Purple gradient header
   - Stats dashboard
   - Platform cards
   - KPI lists
   - Recommendations
   - Download options

---

**Status**: ✅ Ready to Use!

**Next**: Run `./start_ngrok.sh` and register agent!
