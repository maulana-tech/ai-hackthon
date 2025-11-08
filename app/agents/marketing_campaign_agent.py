"""
Marketing Campaign Agent - AI-powered campaign generation

Uses Qwen LLM to generate:
- Campaign content and messaging
- Campaign schedule and timeline
- Budget allocation and recommendations
- Platform-specific strategies

Integrates with:
- Google Sheets for tracking
- Email service for supplier outreach
- GetCirclo for user reporting
"""
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import json

from app.services.sheets_service import sheets_service
from app.services.document_service import document_service
from app.services.campaign_automation_service import campaign_automation
from app.integrations.llm_client import llm_client

logger = logging.getLogger(__name__)


class CampaignRequest(BaseModel):
    """Request model for campaign generation"""
    product_name: str = Field(..., description="Product name")
    product_category: str = Field(..., description="Product category")
    target_audience: Optional[str] = Field(None, description="Target audience")
    budget_range: Optional[str] = Field(None, description="Budget range (e.g., 'Rp 1-5 juta')")
    duration_days: Optional[int] = Field(30, description="Campaign duration in days")
    platforms: Optional[List[str]] = Field(None, description="Marketing platforms")


class CampaignResult(BaseModel):
    """Result of campaign generation"""
    product_name: str
    campaign_content: str
    schedule: Dict[str, Any]
    budget_breakdown: Dict[str, Any]
    platforms_strategy: Dict[str, str]
    kpis: List[str]
    recommendations: List[str]
    sheet_url: Optional[str] = None  # Document view URL
    doc_url: Optional[str] = None  # Raw document URL for download
    automation_results: Optional[Dict[str, Any]] = None  # Next steps automation results


class MarketingCampaignAgent:
    """AI Agent for generating and managing marketing campaigns"""
    
    def __init__(self):
        self.sheets = sheets_service
        self.docs = document_service
        self.automation = campaign_automation
        self.llm = llm_client
        
    async def generate_campaign(
        self,
        request: CampaignRequest
    ) -> CampaignResult:
        """
        Generate complete marketing campaign using AI
        
        Flow:
        1. Use Qwen LLM to generate campaign strategy
        2. Create campaign content
        3. Generate schedule
        4. Allocate budget
        5. Store in Google Sheets
        
        Args:
            request: Campaign request with product details
            
        Returns:
            Complete campaign with content, schedule, budget
        """
        try:
            logger.info(f"Generating campaign for: {request.product_name}")
            
            # Step 1: Generate campaign content using Qwen LLM
            campaign_content = await self._generate_campaign_content(request)
            
            # Step 2: Generate schedule
            schedule = await self._generate_schedule(request)
            
            # Step 3: Generate budget breakdown
            budget = await self._generate_budget(request)
            
            # Step 4: Generate platform strategy
            platforms = await self._generate_platform_strategy(request)
            
            # Step 5: Generate KPIs and recommendations
            kpis = await self._generate_kpis(request)
            recommendations = await self._generate_recommendations(request)
            
            # Step 6: Create shareable campaign document (GitHub Gist)
            doc_result = await self.docs.create_campaign_document(
                campaign_name=request.product_name,
                campaign_data={
                    "product": request.product_name,
                    "campaign_content": campaign_content,
                    "budget": budget,
                    "schedule": schedule,
                    "platforms_strategy": platforms,
                    "kpis": kpis,
                    "recommendations": recommendations
                }
            )
            
            doc_url = doc_result.get("doc_url") if doc_result.get("success") else None
            raw_url = doc_result.get("raw_url") if doc_result.get("success") else None
            
            # Step 7: AUTO-EXECUTE NEXT STEPS (Gemini + Qwen)
            logger.info("🤖 Starting automated next steps...")
            automation_result = await self.automation.auto_execute_next_steps(
                campaign_data={
                    "product": request.product_name,
                    "budget": budget,
                    "schedule": schedule,
                    "platforms_strategy": platforms,
                    "kpis": kpis,
                    "recommendations": recommendations
                },
                product_name=request.product_name
            )
            
            result = CampaignResult(
                product_name=request.product_name,
                campaign_content=campaign_content,
                schedule=schedule,
                budget_breakdown=budget,
                platforms_strategy=platforms,
                kpis=kpis,
                recommendations=recommendations,
                sheet_url=doc_url,  # Document view URL
                doc_url=raw_url,  # Raw markdown URL
                automation_results=automation_result  # Next steps automation
            )
            
            logger.info(f"✅ Campaign + Automation completed for {request.product_name}")
            return result
            
        except Exception as e:
            logger.error(f"Campaign generation error: {str(e)}")
            raise
    
    async def _generate_campaign_content(self, request: CampaignRequest) -> str:
        """Generate campaign content using Qwen LLM"""
        try:
            prompt = f"""
You are an expert marketing campaign strategist for Indonesian e-commerce.

Create a compelling marketing campaign for:
**Product**: {request.product_name}
**Category**: {request.product_category}
**Target Audience**: {request.target_audience or 'General Indonesian consumers'}
**Budget**: {request.budget_range or 'Flexible'}

Generate a campaign that includes:
1. Campaign tagline (in Indonesian)
2. Key messaging points
3. Value propositions
4. Call-to-action
5. Content themes

Make it persuasive, culturally relevant for Indonesia, and optimized for conversion.

Format as JSON with keys: tagline, messaging, value_props, cta, themes
"""
            
            response = await self.llm.generate(prompt, temperature=0.7)
            
            # Try to parse as JSON, fallback to text
            try:
                content_json = json.loads(response)
                return json.dumps(content_json, indent=2, ensure_ascii=False)
            except:
                return response
            
        except Exception as e:
            logger.error(f"Content generation error: {str(e)}")
            # Fallback content
            return json.dumps({
                "tagline": f"Dapatkan {request.product_name} Terbaik Sekarang!",
                "messaging": [
                    "Kualitas terjamin",
                    "Harga kompetitif",
                    "Pengiriman cepat"
                ],
                "value_props": ["Produk original", "Garansi resmi", "Customer service 24/7"],
                "cta": "Beli Sekarang!",
                "themes": ["Quality", "Trust", "Value"]
            }, indent=2, ensure_ascii=False)
    
    async def _generate_schedule(self, request: CampaignRequest) -> Dict[str, Any]:
        """Generate campaign schedule using AI"""
        try:
            duration = request.duration_days or 30
            start_date = datetime.now()
            
            prompt = f"""
Create a {duration}-day marketing campaign schedule for {request.product_name}.

Include:
1. Week-by-week activities
2. Content posting schedule
3. Ad campaign phases (Awareness, Consideration, Conversion)
4. Key milestones

Format as JSON with weekly breakdown.
"""
            
            response = await self.llm.generate(prompt, temperature=0.5)
            
            # Try to parse, fallback to structured schedule
            try:
                return json.loads(response)
            except:
                # Fallback structured schedule
                return {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": (start_date + timedelta(days=duration)).strftime("%Y-%m-%d"),
                    "duration_days": duration,
                    "phases": [
                        {
                            "phase": "Awareness",
                            "week": "1-2",
                            "activities": [
                                "Launch teaser campaign",
                                "Social media posts",
                                "Influencer outreach"
                            ]
                        },
                        {
                            "phase": "Consideration",
                            "week": "2-3",
                            "activities": [
                                "Product demo videos",
                                "Customer testimonials",
                                "Limited-time offers"
                            ]
                        },
                        {
                            "phase": "Conversion",
                            "week": "3-4",
                            "activities": [
                                "Flash sales",
                                "Retargeting ads",
                                "Email campaigns"
                            ]
                        }
                    ],
                    "posting_schedule": {
                        "instagram": "Daily at 10:00, 15:00, 19:00",
                        "facebook": "Daily at 12:00, 18:00",
                        "tiktok": "3x per week"
                    }
                }
            
        except Exception as e:
            logger.error(f"Schedule generation error: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_budget(self, request: CampaignRequest) -> Dict[str, Any]:
        """
        Generate budget allocation using Qwen 3 (specialized for calculations)
        
        Qwen 3 is better for:
        - Complex budget calculations
        - Percentage allocations
        - ROI estimations
        """
        try:
            budget_str = request.budget_range or "Rp 5.000.000"
            
            prompt = f"""
You are a marketing budget expert for Indonesian e-commerce campaigns.

Task: Create detailed budget allocation for {request.product_name} campaign.

Budget Details:
- Total Budget: {budget_str}
- Campaign Duration: {request.duration_days} days
- Target Market: Indonesia

Create optimal budget allocation covering:
1. Social media ads (Facebook, Instagram, TikTok)
2. Influencer marketing (micro & macro)
3. Content creation (photos, videos, graphics)
4. Email marketing campaigns
5. Retargeting & remarketing ads

Requirements:
- Calculate exact percentages and amounts
- Ensure all allocations sum to 100%
- Include daily budget calculation
- Add 3-5 budget optimization recommendations
- Consider Indonesian market rates and practices

Return ONLY valid JSON in this exact format:
{{
  "total_budget": "{budget_str}",
  "allocation": {{
    "social_media_ads": {{"percentage": "X%", "amount": "Rp X,XXX,XXX"}},
    "influencer_marketing": {{"percentage": "X%", "amount": "Rp X,XXX,XXX"}},
    "content_creation": {{"percentage": "X%", "amount": "Rp X,XXX,XXX"}},
    "email_marketing": {{"percentage": "X%", "amount": "Rp X,XXX,XXX"}},
    "retargeting": {{"percentage": "X%", "amount": "Rp X,XXX,XXX"}}
  }},
  "daily_budget": "Rp XXX,XXX",
  "recommendations": ["tip1", "tip2", "tip3"]
}}
"""
            
            # Use Qwen 3 specifically for budget calculations
            response = await self.llm.generate_budget(prompt, temperature=0.5, max_tokens=1500)
            
            try:
                return json.loads(response)
            except:
                # Fallback budget allocation
                return {
                    "total_budget": budget_str,
                    "allocation": {
                        "social_media_ads": {
                            "percentage": "40%",
                            "amount": "Rp 2.000.000",
                            "platforms": ["Instagram", "Facebook", "TikTok"]
                        },
                        "influencer_marketing": {
                            "percentage": "25%",
                            "amount": "Rp 1.250.000"
                        },
                        "content_creation": {
                            "percentage": "20%",
                            "amount": "Rp 1.000.000",
                            "items": ["Photos", "Videos", "Graphics"]
                        },
                        "email_marketing": {
                            "percentage": "10%",
                            "amount": "Rp 500.000"
                        },
                        "retargeting": {
                            "percentage": "5%",
                            "amount": "Rp 250.000"
                        }
                    },
                    "daily_budget": "Rp 166.667",
                    "recommendations": [
                        "Start with smaller budgets and scale based on performance",
                        "Focus 60% budget on best performing platform",
                        "Reserve 10% for testing new channels"
                    ]
                }
            
        except Exception as e:
            logger.error(f"Budget generation error: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_platform_strategy(self, request: CampaignRequest) -> Dict[str, str]:
        """Generate platform-specific strategies"""
        platforms = request.platforms or ["Instagram", "Facebook", "TikTok", "Tokopedia"]
        
        prompt = f"""
Create platform-specific marketing strategies for {request.product_name}.

Platforms: {', '.join(platforms)}

For each platform, provide:
1. Content type (video, image, carousel, etc)
2. Posting frequency
3. Best practices
4. Target metrics

Format as JSON with platform as key.
"""
        
        try:
            response = await self.llm.generate(prompt, temperature=0.6)
            try:
                return json.loads(response)
            except:
                # Fallback strategies
                return {
                    "Instagram": "High-quality product photos, Stories, Reels. Post 2x daily. Focus on aesthetics.",
                    "Facebook": "Community engagement, longer posts, video content. Post 1x daily.",
                    "TikTok": "Short viral videos, trends, challenges. Post 3-5x weekly.",
                    "Tokopedia": "Product listings optimization, flash sales, reviews management."
                }
        except Exception as e:
            logger.error(f"Platform strategy error: {str(e)}")
            return {}
    
    async def _generate_kpis(self, request: CampaignRequest) -> List[str]:
        """Generate campaign KPIs"""
        return [
            "Reach: 50,000+ impressions",
            "Engagement Rate: 5%+",
            "Click-Through Rate: 2%+",
            "Conversion Rate: 1%+",
            "ROI: 3x minimum",
            "Cost Per Acquisition: < Rp 50,000"
        ]
    
    async def _generate_recommendations(self, request: CampaignRequest) -> List[str]:
        """Generate campaign recommendations"""
        return [
            "Test multiple ad creatives in first week",
            "Monitor performance daily and optimize",
            "Engage with comments and messages quickly",
            "Use user-generated content for authenticity",
            "Implement retargeting for cart abandoners",
            "Collaborate with micro-influencers for better ROI"
        ]
    
    async def generate_bulk_campaigns(
        self,
        products: List[Dict[str, Any]],
        base_budget: str = "Rp 5.000.000"
    ) -> List[CampaignResult]:
        """
        Generate campaigns for multiple products
        
        Args:
            products: List of product data
            base_budget: Base budget per product
            
        Returns:
            List of campaign results
        """
        campaigns = []
        
        for product in products:
            try:
                request = CampaignRequest(
                    product_name=product.get("name", "Unknown Product"),
                    product_category=product.get("category", "General"),
                    budget_range=base_budget,
                    duration_days=30
                )
                
                campaign = await self.generate_campaign(request)
                campaigns.append(campaign)
                
            except Exception as e:
                logger.error(f"Failed to generate campaign for {product.get('name')}: {str(e)}")
                continue
        
        logger.info(f"✅ Generated {len(campaigns)} campaigns")
        return campaigns


# Global instance
marketing_campaign_agent = MarketingCampaignAgent()
