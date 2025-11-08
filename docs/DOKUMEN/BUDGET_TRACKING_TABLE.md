# 💰 Budget Tracking Table - Google Sheets Format

## Overview

Sistem sekarang auto-generate **comprehensive budget tracking table** untuk setiap campaign. Table ini siap untuk di-copy ke Google Sheets.

---

## 📊 5 Sheets yang Di-Generate

### Sheet 1: 📊 Overview Dashboard
**Purpose**: Campaign summary dan quick stats

```
| Campaign Overview        |                          |
|--------------------------|--------------------------|
| Product                  | [Product Name]           |
| Total Budget             | Rp 5,000,000            |
| Duration                 | 30 days                  |
| Daily Budget             | =B3/B4                   |
|                          |                          |
| Quick Stats              |                          |
| Total Spent              | =SUM('Daily Tracking'!D:D) |
| Remaining Budget         | =B3-B8                   |
| Budget Used %            | =B8/B3                   |
| Days Elapsed             | =COUNTA('Daily Tracking'!A:A)-1 |
| Days Remaining           | =B4-B11                  |
|                          |                          |
| Platform Performance     |                          |
| Platform   | Budget  | Spent  | Remaining | ROI    |
| Instagram  | 1.75M   | =FORMULA | =FORMULA  | =FORMULA |
| Facebook   | 1.25M   | =FORMULA | =FORMULA  | =FORMULA |
| TikTok     | 1.5M    | =FORMULA | =FORMULA  | =FORMULA |
| Tokopedia  | 500K    | =FORMULA | =FORMULA  | =FORMULA |
```

---

### Sheet 2: 📅 Daily Tracking
**Purpose**: Track daily spending dan performance metrics

**Columns**:
1. Date
2. Platform
3. Campaign Type
4. Spent (Rp)
5. Impressions
6. Clicks
7. CTR % (Formula: =F2/E2*100)
8. Conversions
9. Conversion Rate % (Formula: =H2/F2*100)
10. Cost Per Click (Formula: =D2/F2)
11. Cost Per Conversion (Formula: =D2/H2)
12. Revenue (Rp)
13. ROI % (Formula: =(L2-D2)/D2*100)
14. Notes

**Sample Data**:
```
| Date       | Platform  | Type       | Spent   | Impressions | Clicks | CTR  | Conv | Conv Rate | CPC  | CPC  | Revenue   | ROI  | Notes            |
|------------|-----------|------------|---------|-------------|--------|------|------|-----------|------|------|-----------|------|------------------|
| 2025-11-09 | Instagram | Photo Ads  | 175,000 | 12,500      | 625    | 5.0% | 31   | 4.96%     | 280  | 5,645| 930,000   | 431% | Good performance |
| 2025-11-09 | TikTok    | Video Ads  | 150,000 | 18,000      | 900    | 5.0% | 45   | 5.00%     | 167  | 3,333| 1,350,000 | 800% | Viral content    |
```

**Conditional Formatting**:
- CTR: 🟢 >2% | 🟡 1-2% | 🔴 <1%
- Conversion Rate: 🟢 >1% | 🟡 0.5-1% | 🔴 <0.5%
- ROI: 🟢 >200% | 🟡 100-200% | 🔴 <100%

---

### Sheet 3: 🚀 Platform Performance
**Purpose**: Compare performance across all platforms

**Columns**:
1. Platform
2. Total Budget
3. Total Spent (=SUMIF('Daily Tracking'!B:B,A2,'Daily Tracking'!D:D))
4. Remaining (=B2-C2)
5. Budget Used % (=C2/B2)
6. Total Impressions (=SUMIF...)
7. Total Clicks (=SUMIF...)
8. Avg CTR % (=G2/F2*100)
9. Total Conversions (=SUMIF...)
10. Avg Conv Rate % (=I2/G2*100)
11. Total Revenue (=SUMIF...)
12. Total ROI % (=(K2-C2)/C2*100)
13. Status (=IF(L2>200%,"🟢 Excellent",IF(L2>100%,"🟡 Good","🔴 Poor")))

**Example**:
```
| Platform  | Budget    | Spent  | Remaining | Used % | Impressions | Clicks | CTR  | Conv | Conv Rate | Revenue   | ROI  | Status          |
|-----------|-----------|--------|-----------|--------|-------------|--------|------|------|-----------|-----------|------|-----------------|
| Instagram | 1,750,000 | =FORM  | =FORM     | =FORM  | =FORM       | =FORM  | =FORM| =FORM| =FORM     | =FORM     | =FORM| 🟢 Excellent   |
| Facebook  | 1,250,000 | =FORM  | =FORM     | =FORM  | =FORM       | =FORM  | =FORM| =FORM| =FORM     | =FORM     | =FORM| 🟡 Good        |
| TikTok    | 1,500,000 | =FORM  | =FORM     | =FORM  | =FORM       | =FORM  | =FORM| =FORM| =FORM     | =FORM     | =FORM| 🟢 Excellent   |
| Tokopedia |   500,000 | =FORM  | =FORM     | =FORM  | =FORM       | =FORM  | =FORM| =FORM| =FORM     | =FORM     | =FORM| 🟡 Good        |
```

---

### Sheet 4: 💰 Budget Tracking (MAIN SHEET)
**Purpose**: Detailed budget allocation dan spending tracking

#### Section 1: Budget Allocation
```
| Platform  | Allocated Budget | % | Daily Budget | Spent to Date | Remaining | Days Used | Projected Total | Over/Under | Status        |
|-----------|------------------|---|--------------|---------------|-----------|-----------|-----------------|------------|---------------|
| Instagram | 1,750,000        |35%| =B2/30       | =SUMIF(...)   | =B2-E2    | =COUNTIF  | =E2/G2*30       | =H2-B2     | 🟢 On Track   |
| Facebook  | 1,250,000        |25%| =B3/30       | =SUMIF(...)   | =B3-E3    | =COUNTIF  | =E3/G3*30       | =H3-B3     | 🟢 On Track   |
| TikTok    | 1,500,000        |30%| =B4/30       | =SUMIF(...)   | =B4-E4    | =COUNTIF  | =E4/G4*30       | =H4-B4     | 🟢 On Track   |
| Tokopedia |   500,000        |10%| =B5/30       | =SUMIF(...)   | =B5-E5    | =COUNTIF  | =E5/G5*30       | =H5-B5     | 🟢 On Track   |
```

#### Section 2: Weekly Summary
```
|               | Week 1        | Week 2        | Week 3        | Week 4        |
|---------------|---------------|---------------|---------------|---------------|
| Planned Budget| =SUM(B2:B5)/4 | =SUM(B2:B5)/4 | =SUM(B2:B5)/4 | =SUM(B2:B5)/4 |
| Actual Spend  | =SUMIFS(...)  | =SUMIFS(...)  | =SUMIFS(...)  | =SUMIFS(...)  |
| Variance      | =B12-B11      | =C12-C11      | =D12-D11      | =E12-E11      |
| Variance %    | =B13/B11*100  | =C13/C11*100  | =D13/D11*100  | =E13/E11*100  |
```

#### Section 3: Category Breakdown
```
| Category          | Budget    | Spent        | Remaining | % Used      |
|-------------------|-----------|--------------|-----------|-------------|
| Content Creation  | 1,000,000 | =SUMIF(...)  | =B19-C19  | =C19/B19*100|
| Paid Ads          | 3,500,000 | =SUMIF(...)  | =B20-C20  | =C20/B20*100|
| Influencer        |   500,000 | =SUMIF(...)  | =B21-C21  | =C21/B21*100|
```

#### Section 4: Alerts
```
| Alert Type         | Condition            | Status                                    |
|--------------------|----------------------|-------------------------------------------|
| Budget Alert       | Over 80% spent       | =IF(SUM(E2:E5)/SUM(B2:B5)>0.8,"⚠️ WARNING","✅ OK") |
| Pace Alert         | Spending too fast    | =IF(SUM(E2:E5)/(G2*D2)>1.2,"⚠️ TOO FAST","✅ OK")   |
| Performance Alert  | ROI below target     | =IF(AVERAGE('Platform Performance'!L:L)<200,"⚠️ LOW ROI","✅ OK") |
```

---

### Sheet 5: 📈 KPI Dashboard
**Purpose**: Track all key performance indicators

```
| KPI Name          | Target    | Current        | Progress % | Status        | Trend         |
|-------------------|-----------|----------------|------------|---------------|---------------|
| Reach             | 50,000    | =SUM('Daily'!E:E) | =C2/B2*100 | 🟢 Achieved   | =SPARKLINE(...)|
| CTR               | 2%        | =AVERAGE(...)  | =C3/0.02*100| 🟢 Good       | =SPARKLINE(...)|
| Conversion Rate   | 1%        | =AVERAGE(...)  | =C4/0.01*100| 🟢 Good       | =SPARKLINE(...)|
| ROI               | 300%      | =FORMULA       | =C5/3      | 🟢 Excellent  | =SPARKLINE(...)|
| Cost Per Conv     | 50,000    | =AVERAGE(...)  | =(50000-C6)/50000*100 | 🟢 Good | =SPARKLINE(...)|
```

---

## 🎯 How to Use

### Option 1: Copy-Paste ke Google Sheets

1. **Create new Google Sheets**
2. **Copy structure dari automation result**
3. **Paste ke sheets**
4. **Add formulas** sesuai template
5. **Input daily data** di "Daily Tracking" sheet
6. **Watch automatic calculations!**

### Option 2: Import CSV (Coming Soon)

Will generate CSV export untuk direct import.

---

## 💡 Key Features

### 1. Automatic Calculations
- ✅ Total spent auto-sum dari daily tracking
- ✅ Remaining budget auto-calculate
- ✅ ROI auto-compute dari revenue dan spend
- ✅ Budget alerts auto-trigger

### 2. Multi-Platform Tracking
- ✅ Instagram, Facebook, TikTok, Tokopedia
- ✅ Each platform gets allocation percentage
- ✅ Daily budget per platform
- ✅ Performance comparison

### 3. Time-Based Analysis
- ✅ Daily tracking (30 days)
- ✅ Weekly summaries (4 weeks)
- ✅ Projected totals based on pace
- ✅ Variance analysis

### 4. Category Breakdown
- ✅ Content creation budget
- ✅ Paid ads budget
- ✅ Influencer budget
- ✅ Track spending per category

### 5. Smart Alerts
- ✅ Budget warning at 80%
- ✅ Pace alert if spending too fast
- ✅ ROI alert if below target
- ✅ Visual status indicators

---

## 📊 Budget Allocation (Default)

Total Budget: **Rp 5,000,000**

| Platform  | Allocation | Amount        | Daily Budget |
|-----------|------------|---------------|--------------|
| Instagram | 35%        | Rp 1,750,000  | Rp 58,333    |
| Facebook  | 25%        | Rp 1,250,000  | Rp 41,667    |
| TikTok    | 30%        | Rp 1,500,000  | Rp 50,000    |
| Tokopedia | 10%        | Rp   500,000  | Rp 16,667    |

---

## 🔄 What User Gets

When campaign is generated, user receives:

```
🤖 Next Steps Auto-Executed!

✅ Review: Campaign readiness score 8/10
✅ Budget: Optimized untuk Instagram, TikTok
✅ Content Calendar: 30 posts generated
✅ Tracking: Budget tracking table generated

💰 Budget Allocation:
   • Instagram: 35% (Rp 1,750,000)
   • Facebook: 25% (Rp 1,250,000)
   • TikTok: 30% (Rp 1,500,000)
   • Tokopedia: 10% (Rp 500,000)

✅ Launch Checklist: 12 tasks ready
```

User can then:
1. Click Google Sheets link
2. Create new sheet
3. Copy-paste structure dari document
4. Start tracking campaign performance!

---

## 📱 Mobile-Friendly

All formulas work on:
- ✅ Google Sheets web
- ✅ Google Sheets mobile app
- ✅ Excel (with minor adjustments)

---

**Status**: ✅ Fully Implemented & Ready to Use!
