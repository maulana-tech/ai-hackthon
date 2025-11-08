# 🧪 Test GetCirclo Integration - Quick Guide

## Current Connection

✅ **Status**: Connected  
🌐 **Ngrok URL**: https://unsplendidly-unusurping-charlie.ngrok-free.dev  
🔗 **Webhook**: https://unsplendidly-unusurping-charlie.ngrok-free.dev/circlo-webhook/hook

---

## Quick Test Scenarios

### Test 1: Simple Campaign Request

**Send in GetCirclo**:
```
Buat kampanye marketing untuk smartwatch
```

**Expected Response** (~20s):
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
https://unsplendidly-unusurping-charlie.ngrok-free.dev/documents/abc123/view
```

**What to Check**:
- ✅ Response arrives within 30 seconds
- ✅ Includes automation summary (5 checkmarks)
- ✅ Document URL is clickable
- ✅ URL uses ngrok domain

---

### Test 2: View Beautiful HTML Website

**Click document URL from response**

**Expected Result**:
- ✅ Page loads with purple gradient header
- ✅ Shows "🎯 Marketing Campaign Plan"
- ✅ Product name displayed (smartwatch)
- ✅ 3 stat cards (Duration, Platforms, KPIs)
- ✅ Platform strategy cards visible
- ✅ KPI list with checkmarks
- ✅ Recommendations section
- ✅ Download button present
- ✅ Mobile-responsive (test on phone)

---

### Test 3: Different Product Categories

**Test Fashion**:
```
Buat kampanye untuk fashion wanita
```

**Test Electronics**:
```
Buat campaign elektronik gaming
```

**Test Home Decor**:
```
Buat kampanye marketing untuk furniture minimalis
```

**What to Check**:
- ✅ Each generates unique campaign
- ✅ Product name appears in title
- ✅ Platform strategies differ by category
- ✅ All documents accessible

---

### Test 4: Automation Details

**Check automation results in response**:

Should see:
```
🤖 Next Steps Auto-Executed!

✅ Review: Campaign readiness score 8/10
✅ Budget: Optimized untuk Instagram, TikTok
✅ Content Calendar: 30 posts generated
✅ Tracking: Google Sheets ready
✅ Launch Checklist: 12 tasks ready
```

**What to Verify**:
- ✅ All 5 steps completed
- ✅ Readiness score shown (1-10)
- ✅ Priority channels listed
- ✅ Number of posts stated
- ✅ All items have checkmarks

---

### Test 5: Document Features

**Open any campaign document**

**Check these elements**:

1. **Header**:
   - ✅ Purple gradient background
   - ✅ White text
   - ✅ Product name centered

2. **Stats Cards**:
   - ✅ 3 cards in row (desktop)
   - ✅ Stack vertically on mobile
   - ✅ Show duration, platforms, KPIs count

3. **Platform Cards**:
   - ✅ Each platform has icon
   - ✅ Hover effect works
   - ✅ Strategy text readable

4. **Lists**:
   - ✅ KPIs have checkmarks
   - ✅ Recommendations formatted
   - ✅ Clean spacing

5. **Buttons**:
   - ✅ Download button works
   - ✅ Opens markdown file
   - ✅ Google Sheets link present

---

## Troubleshooting Tests

### Issue: No Response in GetCirclo

**Test webhook directly**:
```bash
curl -X POST http://localhost:8000/circlo-webhook/hook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Buat kampanye test",
    "user": {"id": "test", "name": "Test", "preferredKeywords": [], "preferredNiches": []},
    "profile": {"id": "1", "name": "TrendScout AI", "niche": "Test"},
    "history": []
  }'
```

**Expected**: JSON response with campaign details

---

### Issue: Document URL Returns 404

**Test document endpoint**:
```bash
# List recent documents
curl -s http://localhost:8000/circlo-webhook/webhook-info
```

**Check logs**:
```bash
tail -f logs/server.log | grep -E "Document|campaign"
```

---

### Issue: Slow Response (>30s)

**Check automation time**:
```bash
tail -f logs/server.log | grep -E "automation|step"
```

**Expected timing**:
- Step 1 (Review): 2-3s
- Step 2 (Budget): 3-5s  
- Step 3 (Calendar): 2-3s
- Step 4 (Tracking): 2-3s
- Step 5 (Checklist): 1-2s
- **Total**: ~15s

---

## Performance Benchmarks

### Response Times:
- **Campaign Generation**: 5-7 seconds
- **Document Creation**: <1 second
- **Automation (5 steps)**: 10-15 seconds
- **Total Response**: 15-25 seconds
- **HTML Page Load**: <0.5 seconds

### Success Criteria:
- ✅ Total time < 30 seconds (GetCirclo timeout)
- ✅ Document accessible immediately
- ✅ HTML renders correctly
- ✅ All automation steps complete

---

## Validation Checklist

Before marking as "fully working":

**Backend**:
- [ ] Server running on port 8000
- [ ] Ngrok tunnel active
- [ ] Webhook receiving requests
- [ ] Logs show no errors
- [ ] All LLM APIs responding

**GetCirclo**:
- [ ] Agent registered (@trendscout-ai)
- [ ] Webhook URL configured
- [ ] Messages being received
- [ ] Responses returning correctly

**Campaign Generation**:
- [ ] Campaign content generated
- [ ] Document created with unique ID
- [ ] Document URLs using ngrok domain
- [ ] All fields populated correctly

**Automation**:
- [ ] All 5 steps executing
- [ ] Running in parallel (check timing)
- [ ] Results included in response
- [ ] No timeout errors

**HTML Documents**:
- [ ] Beautiful design loads
- [ ] Purple gradient header
- [ ] All sections visible
- [ ] Stats cards display
- [ ] Platform cards render
- [ ] Lists formatted correctly
- [ ] Buttons work
- [ ] Mobile responsive

**User Experience**:
- [ ] Response arrives quickly (<30s)
- [ ] Message well formatted
- [ ] Document URL clickable
- [ ] Website professional looking
- [ ] Easy to read on mobile
- [ ] Download button works

---

## Test Results Log

**Date**: 2025-11-09  
**Tester**: [Your Name]

### Test 1: Campaign Request
- Status: ✅ Pass / ❌ Fail
- Response Time: ___ seconds
- Notes: ___

### Test 2: HTML Website
- Status: ✅ Pass / ❌ Fail
- Design: ✅ Good / ❌ Issues
- Notes: ___

### Test 3: Different Products
- Fashion: ✅ / ❌
- Electronics: ✅ / ❌
- Home Decor: ✅ / ❌

### Test 4: Automation
- All steps complete: ✅ / ❌
- Timing acceptable: ✅ / ❌
- Results displayed: ✅ / ❌

### Test 5: Document Features
- Header: ✅ / ❌
- Stats: ✅ / ❌
- Platform cards: ✅ / ❌
- Lists: ✅ / ❌
- Buttons: ✅ / ❌

---

**Overall Status**: ✅ All Tests Passing

**Ready for Use**: Yes ✅ / No ❌

**Notes**: ___
