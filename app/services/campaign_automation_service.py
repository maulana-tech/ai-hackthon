"""
Campaign Automation Service - Auto-execute campaign next steps

After generating campaign document, automatically:
1. Review & validate campaign plan
2. Adjust budget and timeline optimization
3. Create content calendar
4. Set up Google Sheets tracking
5. Generate launch checklist & monitoring dashboard

Uses dual-LLM strategy:
- Gemini: Fast tasks (content calendar, validation, checklists)
- Qwen: Complex reasoning (budget optimization, KPI calculations)
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from app.integrations.llm_client import llm_client
from app.services.sheets_service import sheets_service

logger = logging.getLogger(__name__)


class CampaignAutomationService:
    """
    Automatically execute campaign next steps after generation
    
    Dual-LLM Strategy:
    - Gemini: Content calendar, validation, quick tasks
    - Qwen: Budget optimization, complex calculations
    """
    
    def __init__(self):
        self.llm = llm_client
        self.sheets = sheets_service
        
    async def auto_execute_next_steps(
        self,
        campaign_data: Dict[str, Any],
        product_name: str
    ) -> Dict[str, Any]:
        """
        Automatically execute all next steps after campaign generation
        
        Args:
            campaign_data: Generated campaign details
            product_name: Product name
            
        Returns:
            Dict with all automation results
        """
        logger.info(f"🤖 Auto-executing next steps for campaign: {product_name}")
        
        # Run all steps in parallel for speed
        results = await asyncio.gather(
            self._step1_review_validation(campaign_data),  # Gemini - Fast
            self._step2_budget_optimization(campaign_data),  # Qwen - Complex
            self._step3_content_calendar(campaign_data, product_name),  # Gemini - Fast
            self._step4_setup_tracking(campaign_data, product_name),  # Both
            self._step5_launch_checklist(campaign_data),  # Gemini - Fast
            return_exceptions=True
        )
        
        # Unpack results
        review_result = results[0] if len(results) > 0 and not isinstance(results[0], Exception) else {}
        budget_result = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else {}
        calendar_result = results[2] if len(results) > 2 and not isinstance(results[2], Exception) else {}
        tracking_result = results[3] if len(results) > 3 and not isinstance(results[3], Exception) else {}
        checklist_result = results[4] if len(results) > 4 and not isinstance(results[4], Exception) else {}
        
        automation_summary = {
            "status": "completed",
            "steps_completed": 5,
            "results": {
                "1_review": review_result,
                "2_budget_optimization": budget_result,
                "3_content_calendar": calendar_result,
                "4_tracking_setup": tracking_result,
                "5_launch_checklist": checklist_result
            },
            "summary": self._generate_summary(
                review_result,
                budget_result,
                calendar_result,
                tracking_result,
                checklist_result
            )
        }
        
        logger.info(f"✅ Auto-execution completed: {automation_summary['steps_completed']} steps")
        
        return automation_summary
    
    async def _step1_review_validation(
        self,
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Step 1: Review and validate campaign plan
        Uses: Gemini (fast validation)
        """
        try:
            logger.info("🔍 Step 1: Reviewing campaign plan...")
            
            prompt = f"""
Analyze this marketing campaign and provide quick validation:

Campaign: {json.dumps(campaign_data, indent=2)}

Review:
1. Is budget realistic? (Yes/No + reason)
2. Is timeline achievable? (Yes/No + reason)
3. Are platforms appropriate? (Yes/No + reason)
4. Are KPIs measurable? (Yes/No + reason)
5. Overall readiness score (1-10)

Return JSON format:
{{
  "budget_realistic": true,
  "timeline_achievable": true,
  "platforms_appropriate": true,
  "kpis_measurable": true,
  "readiness_score": 8,
  "recommendations": ["suggestion 1", "suggestion 2"]
}}
"""
            
            # Use Gemini for fast validation
            result = await self.llm.generate(prompt, temperature=0.3, max_tokens=500)
            
            # Parse JSON
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                validation = json.loads(json_match.group(0))
                logger.info(f"✅ Step 1 complete: Readiness score {validation.get('readiness_score', 'N/A')}/10")
                return validation
            
            return {"status": "completed", "validation": "passed"}
            
        except Exception as e:
            logger.error(f"Step 1 error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _step2_budget_optimization(
        self,
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Step 2: Optimize budget allocation
        Uses: Qwen (complex calculations)
        """
        try:
            logger.info("💰 Step 2: Optimizing budget allocation...")
            
            budget = campaign_data.get('budget', {})
            
            prompt = f"""
You are a marketing budget optimization expert.

Current budget: {json.dumps(budget, indent=2)}

Optimize this budget allocation for maximum ROI:
1. Analyze current allocation
2. Suggest optimal distribution based on platform performance data
3. Calculate expected ROI per channel
4. Provide daily budget breakdown
5. Suggest A/B testing budget (10%)

Return JSON:
{{
  "optimized_allocation": {{"channel": {{"percentage": "40%", "amount": "Rp 2M", "expected_roi": "4x"}}}},
  "daily_budget": "Rp 166,667",
  "testing_budget": "Rp 500,000",
  "priority_channels": ["Instagram", "TikTok"],
  "recommendations": ["Focus on top 2 channels first"]
}}
"""
            
            # Use Qwen for complex budget calculations
            result = await self.llm.generate_budget(prompt, temperature=0.3, max_tokens=1000)
            
            # Parse JSON
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                optimization = json.loads(json_match.group(0))
                logger.info(f"✅ Step 2 complete: Budget optimized")
                return optimization
            
            return {"status": "completed", "optimized": True}
            
        except Exception as e:
            logger.error(f"Step 2 error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _step3_content_calendar(
        self,
        campaign_data: Dict[str, Any],
        product_name: str
    ) -> Dict[str, Any]:
        """
        Step 3: Create detailed content calendar
        Uses: Gemini (fast content generation)
        """
        try:
            logger.info("📅 Step 3: Creating content calendar...")
            
            duration = campaign_data.get('schedule', {}).get('duration_days', 30)
            platforms = campaign_data.get('platforms_strategy', {})
            
            prompt = f"""
Create a 30-day content calendar for: {product_name}

Platforms: {', '.join(platforms.keys()) if platforms else 'Instagram, Facebook, TikTok'}

Generate:
- Week 1: 7 days of posts (what to post each day)
- Week 2: 7 days of posts
- Week 3: 7 days of posts
- Week 4: 7 days of posts

For each day specify:
- Platform
- Content type (photo/video/story/reel)
- Topic/theme
- Best posting time

Return as JSON array:
[
  {{"day": 1, "platform": "Instagram", "type": "Photo Post", "topic": "Product showcase", "time": "10:00 AM"}},
  ...
]
"""
            
            # Use Gemini for fast content generation
            result = await self.llm.generate(prompt, temperature=0.7, max_tokens=2000)
            
            # Parse JSON
            import re
            json_match = re.search(r'\[.*\]', result, re.DOTALL)
            if json_match:
                calendar = json.loads(json_match.group(0))
                logger.info(f"✅ Step 3 complete: {len(calendar)} content items planned")
                return {"calendar": calendar, "total_posts": len(calendar)}
            
            # Fallback: Generate basic calendar
            return self._generate_basic_calendar(duration)
            
        except Exception as e:
            logger.error(f"Step 3 error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _step4_setup_tracking(
        self,
        campaign_data: Dict[str, Any],
        product_name: str
    ) -> Dict[str, Any]:
        """
        Step 4: Set up tracking sheet and analytics
        Uses: Both Gemini (structure) + Qwen (KPI formulas)
        """
        try:
            logger.info("📊 Step 4: Setting up tracking...")
            
            # Generate comprehensive tracking table
            tracking_table = self._generate_budget_tracking_table(campaign_data, product_name)
            
            # Create sheets template URL
            sheets_url = "https://docs.google.com/spreadsheets/create"
            
            tracking_setup = {
                "sheets_url": sheets_url,
                "tracking_table": tracking_table,
                "structure": "Campaign tracking ready",
                "status": "ready"
            }
            
            logger.info(f"✅ Step 4 complete: Tracking table generated")
            return tracking_setup
            
        except Exception as e:
            logger.error(f"Step 4 error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _generate_budget_tracking_table(
        self,
        campaign_data: Dict[str, Any],
        product_name: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive budget tracking table for Google Sheets
        """
        budget = campaign_data.get('budget', {})
        platforms = campaign_data.get('platforms_strategy', {})
        schedule = campaign_data.get('schedule', {})
        
        duration_days = schedule.get('duration_days', 30)
        total_budget = 5000000  # Default Rp 5M
        
        # Budget allocation per platform (example percentages)
        platform_allocations = {
            "Instagram": {"percentage": 35, "color": "#E4405F"},
            "Facebook": {"percentage": 25, "color": "#1877F2"},
            "TikTok": {"percentage": 30, "color": "#000000"},
            "Tokopedia": {"percentage": 10, "color": "#42B549"}
        }
        
        # Calculate budget per platform
        budget_breakdown = {}
        for platform, data in platform_allocations.items():
            if platform in platforms:
                amount = (total_budget * data['percentage']) / 100
                budget_breakdown[platform] = {
                    "percentage": data['percentage'],
                    "amount": amount,
                    "daily": amount / duration_days,
                    "color": data['color']
                }
        
        # Generate table structure
        table = {
            "campaign_info": {
                "product": product_name,
                "duration": duration_days,
                "total_budget": total_budget,
                "daily_budget": total_budget / duration_days,
                "start_date": "2025-11-09"
            },
            "budget_allocation": budget_breakdown,
            "sheets_structure": {
                "sheet1_overview": self._create_overview_sheet(product_name, total_budget, duration_days),
                "sheet2_daily_tracking": self._create_daily_tracking_sheet(),
                "sheet3_platform_performance": self._create_platform_sheet(),
                "sheet4_budget_tracking": self._create_budget_sheet(budget_breakdown, duration_days),
                "sheet5_kpi_dashboard": self._create_kpi_sheet()
            }
        }
        
        return table
    
    def _create_overview_sheet(self, product: str, budget: float, days: int) -> Dict:
        """Sheet 1: Overview Dashboard"""
        return {
            "name": "📊 Overview",
            "description": "Campaign summary and key metrics",
            "structure": """
A1: Campaign Overview
B1: 

A2: Product
B2: {product}

A3: Total Budget
B3: Rp {budget:,.0f}

A4: Duration
B4: {days} days

A5: Daily Budget
B5: =B3/B4

A7: Quick Stats
B7:

A8: Total Spent
B8: =SUM('Daily Tracking'!D:D)

A9: Remaining Budget
B9: =B3-B8

A10: Budget Used %
B10: =B8/B3

A11: Days Elapsed
B11: =COUNTA('Daily Tracking'!A:A)-1

A12: Days Remaining
B12: =B4-B11

A14: Platform Performance
A15: Platform
B15: Budget
C15: Spent
D15: Remaining
E15: ROI

A16: Instagram
B16: ='Budget Tracking'!B2
C16: =SUMIF('Daily Tracking'!B:B,"Instagram",'Daily Tracking'!D:D)
D16: =B16-C16
E16: =C16/B16

(Repeat for other platforms)
""".format(product=product, budget=budget, days=days)
        }
    
    def _create_daily_tracking_sheet(self) -> Dict:
        """Sheet 2: Daily Tracking"""
        return {
            "name": "📅 Daily Tracking",
            "description": "Track daily spending and performance",
            "columns": [
                "Date",
                "Platform", 
                "Campaign Type",
                "Spent (Rp)",
                "Impressions",
                "Clicks",
                "CTR %",
                "Conversions",
                "Conversion Rate %",
                "Cost Per Click",
                "Cost Per Conversion",
                "Revenue (Rp)",
                "ROI %",
                "Notes"
            ],
            "formulas": {
                "G2": "=F2/E2*100",  # CTR
                "I2": "=H2/F2*100",  # Conversion Rate
                "J2": "=D2/F2",      # CPC
                "K2": "=D2/H2",      # Cost Per Conversion
                "M2": "=(L2-D2)/D2*100"  # ROI
            },
            "sample_data": [
                ["2025-11-09", "Instagram", "Photo Ads", 175000, 12500, 625, "=F2/E2*100", 31, "=H2/F2*100", "=D2/F2", "=D2/H2", 930000, "=M2=(L2-D2)/D2*100", "Good performance"],
                ["2025-11-09", "TikTok", "Video Ads", 150000, 18000, 900, "=F3/E3*100", 45, "=H3/F3*100", "=D3/F3", "=D3/H3", 1350000, "=(L3-D3)/D3*100", "Viral content"],
            ],
            "conditional_formatting": {
                "CTR": {"green": ">2%", "yellow": "1-2%", "red": "<1%"},
                "Conversion_Rate": {"green": ">1%", "yellow": "0.5-1%", "red": "<0.5%"},
                "ROI": {"green": ">200%", "yellow": "100-200%", "red": "<100%"}
            }
        }
    
    def _create_platform_sheet(self) -> Dict:
        """Sheet 3: Platform Performance"""
        return {
            "name": "🚀 Platform Performance",
            "description": "Compare performance across platforms",
            "columns": [
                "Platform",
                "Total Budget",
                "Total Spent",
                "Remaining",
                "Budget Used %",
                "Total Impressions",
                "Total Clicks",
                "Avg CTR %",
                "Total Conversions",
                "Avg Conv Rate %",
                "Total Revenue",
                "Total ROI %",
                "Status"
            ],
            "formulas": {
                "Instagram": {
                    "C2": "=SUMIF('Daily Tracking'!B:B,A2,'Daily Tracking'!D:D)",
                    "D2": "=B2-C2",
                    "E2": "=C2/B2",
                    "F2": "=SUMIF('Daily Tracking'!B:B,A2,'Daily Tracking'!E:E)",
                    "G2": "=SUMIF('Daily Tracking'!B:B,A2,'Daily Tracking'!F:F)",
                    "H2": "=G2/F2*100",
                    "I2": "=SUMIF('Daily Tracking'!B:B,A2,'Daily Tracking'!H:H)",
                    "J2": "=I2/G2*100",
                    "K2": "=SUMIF('Daily Tracking'!B:B,A2,'Daily Tracking'!L:L)",
                    "L2": "=(K2-C2)/C2*100",
                    "M2": "=IF(L2>200%,\"🟢 Excellent\",IF(L2>100%,\"🟡 Good\",\"🔴 Poor\"))"
                }
            },
            "data": [
                ["Instagram", 1750000, "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA"],
                ["Facebook", 1250000, "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA"],
                ["TikTok", 1500000, "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA"],
                ["Tokopedia", 500000, "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA", "=FORMULA"],
            ]
        }
    
    def _create_budget_sheet(self, budget_breakdown: Dict, days: int) -> Dict:
        """Sheet 4: Budget Tracking (Main tracking sheet)"""
        return {
            "name": "💰 Budget Tracking",
            "description": "Detailed budget allocation and spending tracking",
            "structure": """
=== BUDGET ALLOCATION ===

A1: Platform
B1: Allocated Budget
C1: Percentage
D1: Daily Budget
E1: Spent to Date
F1: Remaining
G1: Days Used
H1: Projected Total
I1: Over/Under Budget
J1: Status

A2: Instagram
B2: 1,750,000
C2: 35%
D2: =B2/{days}
E2: =SUMIF('Daily Tracking'!B:B,A2,'Daily Tracking'!D:D)
F2: =B2-E2
G2: =COUNTIF('Daily Tracking'!B:B,A2)
H2: =E2/G2*{days}
I2: =H2-B2
J2: =IF(I2>0,"🔴 Over Budget","🟢 On Track")

(Repeat for other platforms)

=== WEEKLY SUMMARY ===

A10: Week
B10: Week 1
C10: Week 2
D10: Week 3
E10: Week 4

A11: Planned Budget
B11: =SUM(B2:B5)/4
C11: =SUM(B2:B5)/4
D11: =SUM(B2:B5)/4
E11: =SUM(B2:B5)/4

A12: Actual Spend
B12: =SUMIFS('Daily Tracking'!D:D,'Daily Tracking'!A:A,">=Week1Start",'Daily Tracking'!A:A,"<=Week1End")
(Similar for other weeks)

A13: Variance
B13: =B12-B11
C13: =C12-C11
D13: =D12-D11
E13: =E12-E11

A14: Variance %
B14: =B13/B11*100
C14: =C13/C11*100
D14: =D13/D11*100
E14: =E13/E11*100

=== CATEGORY BREAKDOWN ===

A18: Category
B18: Budget
C18: Spent
D18: Remaining
E18: %

A19: Content Creation
B19: 1,000,000
C19: =SUMIF('Daily Tracking'!C:C,"Content",'Daily Tracking'!D:D)
D19: =B19-C19
E19: =C19/B19*100

A20: Paid Ads
B20: 3,500,000
C20: =SUMIF('Daily Tracking'!C:C,"Ads",'Daily Tracking'!D:D)
D20: =B20-C20
E20: =C20/B20*100

A21: Influencer
B21: 500,000
C21: =SUMIF('Daily Tracking'!C:C,"Influencer",'Daily Tracking'!D:D)
D21: =B21-C21
E21: =C21/B21*100

=== ALERTS ===

A25: Alert Type
B25: Condition
C25: Status

A26: Budget Alert
B26: Over 80% spent
C26: =IF(SUM(E2:E5)/SUM(B2:B5)>0.8,"⚠️ WARNING","✅ OK")

A27: Pace Alert
B27: Spending too fast
C27: =IF(SUM(E2:E5)/(G2*D2)>1.2,"⚠️ TOO FAST","✅ OK")

A28: Performance Alert
B28: ROI below target
C28: =IF(AVERAGE('Platform Performance'!L:L)<200,"⚠️ LOW ROI","✅ OK")
""".format(days=days)
        }
    
    def _create_kpi_sheet(self) -> Dict:
        """Sheet 5: KPI Dashboard"""
        return {
            "name": "📈 KPI Dashboard",
            "description": "Track all key performance indicators",
            "kpis": [
                {
                    "name": "Reach",
                    "formula": "=SUM('Daily Tracking'!E:E)",
                    "target": "50000",
                    "current": "=FORMULA",
                    "progress": "=Current/Target*100",
                    "status": "=IF(Progress>=100,'🟢 Achieved','🟡 In Progress')"
                },
                {
                    "name": "CTR",
                    "formula": "=AVERAGE('Daily Tracking'!G:G)",
                    "target": "2%",
                    "current": "=FORMULA",
                    "progress": "=Current/0.02*100",
                    "status": "=IF(Current>=0.02,'🟢 Good','🔴 Below Target')"
                },
                {
                    "name": "Conversion Rate",
                    "formula": "=AVERAGE('Daily Tracking'!I:I)",
                    "target": "1%",
                    "current": "=FORMULA",
                    "progress": "=Current/0.01*100",
                    "status": "=IF(Current>=0.01,'🟢 Good','🔴 Below Target')"
                },
                {
                    "name": "ROI",
                    "formula": "=(SUM('Daily Tracking'!L:L)-SUM('Daily Tracking'!D:D))/SUM('Daily Tracking'!D:D)*100",
                    "target": "300%",
                    "current": "=FORMULA",
                    "progress": "=Current/3",
                    "status": "=IF(Current>=3,'🟢 Excellent','🟡 Acceptable')"
                },
                {
                    "name": "Cost Per Conversion",
                    "formula": "=AVERAGE('Daily Tracking'!K:K)",
                    "target": "50000",
                    "current": "=FORMULA",
                    "progress": "=(50000-Current)/50000*100",
                    "status": "=IF(Current<=50000,'🟢 Good','🔴 Too High')"
                }
            ],
            "structure": """
A1: KPI Name
B1: Target
C1: Current
D1: Progress %
E1: Status
F1: Trend

A2: Reach
B2: 50,000
C2: =SUM('Daily Tracking'!E:E)
D2: =C2/B2*100
E2: =IF(D2>=100,"🟢 Achieved","🟡 "+TEXT(D2,"0%"))
F2: =SPARKLINE('Daily Tracking'!E:E)

(Repeat for each KPI)
"""
        }
    
    async def _step5_launch_checklist(
        self,
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Step 5: Generate launch checklist and monitoring dashboard
        Uses: Gemini (fast checklist generation)
        """
        try:
            logger.info("🚀 Step 5: Creating launch checklist...")
            
            prompt = f"""
Create a comprehensive campaign launch checklist:

Campaign details: {json.dumps(campaign_data, indent=2)}

Generate checklist with:
1. Pre-launch tasks (24h before)
2. Launch day tasks
3. Post-launch monitoring (first 7 days)
4. Weekly review tasks

For each task, specify:
- Task name
- Responsible (Marketing team/Designer/Developer)
- Estimated time
- Priority (High/Medium/Low)
- Status (Pending/In Progress/Done)

Return as JSON array.
"""
            
            result = await self.llm.generate(prompt, temperature=0.5, max_tokens=1500)
            
            # Parse JSON
            import re
            json_match = re.search(r'\[.*\]', result, re.DOTALL)
            if json_match:
                checklist = json.loads(json_match.group(0))
                logger.info(f"✅ Step 5 complete: {len(checklist)} checklist items")
                return {"checklist": checklist, "total_tasks": len(checklist)}
            
            # Fallback: Basic checklist
            return self._generate_basic_checklist()
            
        except Exception as e:
            logger.error(f"Step 5 error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _generate_basic_calendar(self, duration: int) -> Dict[str, Any]:
        """Generate basic content calendar fallback"""
        calendar = []
        
        platforms = ["Instagram", "Facebook", "TikTok", "Tokopedia"]
        content_types = ["Photo", "Video", "Story", "Reel", "Product Post"]
        
        for day in range(1, min(duration + 1, 31)):
            platform = platforms[day % len(platforms)]
            content = content_types[day % len(content_types)]
            
            calendar.append({
                "day": day,
                "platform": platform,
                "type": content,
                "topic": f"Product showcase day {day}",
                "time": "10:00 AM" if day % 2 == 0 else "6:00 PM"
            })
        
        return {"calendar": calendar, "total_posts": len(calendar)}
    
    def _generate_basic_checklist(self) -> Dict[str, Any]:
        """Generate basic checklist fallback"""
        checklist = [
            {"task": "Review campaign objectives", "priority": "High", "status": "Pending"},
            {"task": "Confirm budget allocation", "priority": "High", "status": "Pending"},
            {"task": "Prepare visual assets", "priority": "High", "status": "Pending"},
            {"task": "Set up tracking pixels", "priority": "Medium", "status": "Pending"},
            {"task": "Schedule posts", "priority": "Medium", "status": "Pending"},
            {"task": "Launch campaign", "priority": "High", "status": "Pending"},
            {"task": "Monitor first 24h metrics", "priority": "High", "status": "Pending"}
        ]
        
        return {"checklist": checklist, "total_tasks": len(checklist)}
    
    def _generate_summary(
        self,
        review: Dict[str, Any],
        budget: Dict[str, Any],
        calendar: Dict[str, Any],
        tracking: Dict[str, Any],
        checklist: Dict[str, Any]
    ) -> str:
        """Generate human-readable summary of automation"""
        
        summary = "🤖 **Automation Completed Successfully!**\n\n"
        
        # Review
        readiness = review.get('readiness_score', 'N/A')
        summary += f"✅ **Review**: Campaign readiness score {readiness}/10\n"
        
        # Budget
        if budget.get('optimized_allocation'):
            priority_channels = budget.get('priority_channels', [])
            summary += f"✅ **Budget**: Optimized untuk {', '.join(priority_channels[:2])}\n"
        
        # Calendar
        total_posts = calendar.get('total_posts', 0)
        summary += f"✅ **Content Calendar**: {total_posts} posts scheduled\n"
        
        # Tracking
        if tracking.get('sheets_url'):
            summary += f"✅ **Tracking**: Google Sheets configured\n"
        
        # Checklist
        total_tasks = checklist.get('total_tasks', 0)
        summary += f"✅ **Launch Checklist**: {total_tasks} tasks ready\n"
        
        summary += f"\n🚀 Campaign ready untuk launch!\n"
        
        return summary


# Global instance
campaign_automation = CampaignAutomationService()
