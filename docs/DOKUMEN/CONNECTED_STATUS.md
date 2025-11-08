# ✅ GetCirclo Connection - ACTIVE!

**Status**: Connected & Running  
**Date**: 2025-11-09  
**Mode**: Ngrok Tunnel

---

## 🌐 Current URLs

```
Ngrok Public URL:
https://unsplendidly-unusurping-charlie.ngrok-free.dev

GetCirclo Webhook:
https://unsplendidly-unusurping-charlie.ngrok-free.dev/circlo-webhook/hook

Local Server:
http://localhost:8000
```

---

## 📊 System Status

| Component | Status | Details |
|-----------|--------|---------|
| FastAPI Server | ✅ Running | Port 8000 |
| Ngrok Tunnel | ✅ Active | Public HTTPS |
| GetCirclo Agent | ✅ Registered | @trendscout-ai |
| Webhook Endpoint | ✅ Working | Receiving messages |
| Document Service | ✅ Working | Beautiful HTML |
| Automation | ✅ Active | 5 steps (Gemini + Qwen) |
| Campaign Generation | ✅ Working | ~20s response time |

---

## 🎯 How to Use

### In GetCirclo App:

1. **Search for agent**: `@trendscout-ai`

2. **Send message**:
   ```
   Buat kampanye marketing untuk smartwatch
   ```

3. **Get response** (~20 seconds):
   ```
   🎯 Kampanye untuk smartwatch sudah siap!
   
   💰 Budget: Rp 5.000.000
   📅 Durasi: 30 hari
   
   🤖 Next Steps Auto-Executed!
   
   ✅ Review: Campaign readiness score 8/10
   ✅ Budget: Optimized untuk Instagram, TikTok
   ✅ Content Calendar: 30 posts generated
   ✅ Tracking: Google Sheets ready
   ✅ Launch Checklist: 12 tasks ready
   
   📄 Campaign Document:
   https://unsplendidly-unusurping-charlie.ngrok-free.dev/documents/abc123/view
   ```

4. **Click document URL** → Opens beautiful HTML website!

---

## 📄 Document Features

When you click the document URL, you'll see:

### 1. Header
- **Purple gradient background**
- Product name as title
- Professional design

### 2. Stats Dashboard
- 📊 Campaign duration (30 days)
- 🚀 Number of platforms (4)
- 📈 KPIs tracked (6+)

### 3. Platform Strategy Cards
Each platform gets its own card:
- 📸 **Instagram**: Strategy details
- 👥 **Facebook**: Strategy details
- 🎵 **TikTok**: Strategy details
- 🛍️ **Tokopedia**: Strategy details

### 4. KPI List
With checkmarks:
- ✓ Reach: 50,000+ impressions
- ✓ Engagement Rate: 5%+
- ✓ Click-Through Rate: 2%+
- ✓ Conversion Rate: 1%+
- ✓ ROI: 3x minimum

### 5. Recommendations
Professional action items:
- ✓ Test multiple ad creatives
- ✓ Monitor performance daily
- ✓ Engage with comments quickly
- ✓ Use user-generated content
- ✓ Implement retargeting

### 6. Action Buttons
- 📥 **Download Markdown** - Get raw file
- 📊 **Create Tracking Sheet** - Google Sheets link

---

## 🤖 Automation Included

Every campaign automatically executes 5 next steps:

### 1. Review & Validation (Gemini)
- Validates budget realism
- Checks timeline feasibility
- Returns readiness score (1-10)
- **Time**: 2-3 seconds

### 2. Budget Optimization (Qwen)
- Calculates optimal allocation
- Estimates ROI per channel
- Daily budget breakdown
- **Time**: 3-5 seconds

### 3. Content Calendar (Gemini)
- 30-day posting schedule
- Platform + content type + topic
- Best posting times
- **Time**: 2-3 seconds

### 4. Tracking Setup (Both)
- Google Sheets structure
- KPI formulas
- Tracking template
- **Time**: 2-3 seconds

### 5. Launch Checklist (Gemini)
- Pre-launch tasks
- Launch day checklist
- Post-launch monitoring
- **Time**: 1-2 seconds

**Total Automation Time**: ~15 seconds (parallel execution)

---

## 🔍 Sample Queries

Try these in GetCirclo:

### Campaign Creation:
```
Buat kampanye marketing untuk smartwatch
Buat kampanye untuk fashion wanita
Buat campaign elektronik
```

### Product Search:
```
Cari produk terlaris fashion
Produk apa yang lagi trending?
Supplier tas di Jakarta
```

### General Help:
```
Gimana cara pakai?
Help
Apa yang bisa kamu lakukan?
```

---

## 📊 Monitoring

### View Logs:
```bash
tail -f /Users/em/web/ai-hackthon/logs/server.log
```

### Check Ngrok Traffic:
```bash
open http://127.0.0.1:4040
# Or visit in browser
```

### Test Webhook Locally:
```bash
curl -X POST http://localhost:8000/circlo-webhook/hook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "test",
    "user": {"id": "1", "name": "Test", "preferredKeywords": [], "preferredNiches": []},
    "profile": {"id": "1", "name": "Agent", "niche": "Test"},
    "history": []
  }'
```

---

## 🛑 To Stop Services

```bash
# Stop all
./stop_services.sh

# Or manually:
lsof -ti:8000 | xargs kill -9
pkill -f ngrok
```

---

## 🔄 If Ngrok URL Changes

**Note**: Free tier ngrok URL changes on restart.

If you restart services:

1. **Get new URL**:
   ```bash
   curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])"
   ```

2. **Re-register agent**:
   ```bash
   export AGENT_WEBHOOK_URL=NEW_NGROK_URL/circlo-webhook/hook
   python3 scripts/register_circlo_agent.py
   ```

3. **Test again** in GetCirclo

---

## ⚡ Quick Commands

```bash
# Start services
./start_ngrok.sh

# Stop services
./stop_services.sh

# View logs
tail -f logs/server.log

# Check status
curl http://localhost:8000/health

# View ngrok dashboard
open http://127.0.0.1:4040
```

---

## 📚 Documentation

- **Full Setup**: `NGROK_GETCIRCLO_SETUP.md`
- **Automation Details**: `DUAL_LLM_STRATEGY.md`
- **System Architecture**: `AUTO_CAMPAIGN_GENERATION.md`
- **GetCirclo API**: `docs/CIRCLO.md`
- **Integration Guide**: `docs/CIRCLO_INTEGRATION.md`

---

## 🎉 Success Indicators

You know it's working when:

1. ✅ User sends message in GetCirclo
2. ✅ Response appears within 20-30 seconds
3. ✅ Response includes automation summary
4. ✅ Document URL is included
5. ✅ Clicking URL opens beautiful HTML website
6. ✅ Website shows campaign details with styling
7. ✅ Download button works
8. ✅ All platform cards display correctly

---

**Status**: ✅ FULLY OPERATIONAL

**Last Updated**: 2025-11-09  
**Connection**: Stable  
**Performance**: Optimal
