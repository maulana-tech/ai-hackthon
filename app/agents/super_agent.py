import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from app.models.schemas import (
    TrendAnalysisRequest,
    SupplierSearchRequest,
    OutreachRequest,
    FinalReport,
    JobStatus
)
from app.agents.trend_analyst import TrendAnalystAgent
from app.agents.supplier_scout import SupplierScoutAgent
from app.agents.outreach_agent import OutreachAgent
from app.agents.memory_keeper import MemoryKeeperAgent
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class SuperAgent:
    """
    Super Agent - Orchestrator that coordinates all sub-agents
    Manages the complete workflow from user query to final report
    """
    
    def __init__(self):
        self.name = "TrendScout Super Agent"
        self.trend_analyst = TrendAnalystAgent()
        self.supplier_scout = SupplierScoutAgent()
        self.outreach_agent = OutreachAgent()
        self.memory_keeper = MemoryKeeperAgent()
        self.jobs = {}
        
    async def execute_full_workflow(
        self,
        query: str,
        user_id: str,
        quantity: int = 20,
        region: str = "global",
        location: Optional[str] = None,
        auto_contact: bool = True
    ) -> FinalReport:
        """
        Execute complete workflow:
        1. Parse user query
        2. Analyze trends
        3. Find suppliers
        4. Contact suppliers (optional)
        5. Generate final report
        6. Save to memory
        """
        
        job_id = str(uuid.uuid4())
        
        logger.info(f"Starting workflow {job_id} for query: {query}")
        
        self.jobs[job_id] = {
            "status": JobStatus.PENDING,
            "progress": 0,
            "message": "Initializing...",
            "created_at": datetime.now()
        }
        
        try:
            preferences = await self.memory_keeper.get_preference(user_id)
            if preferences and not location:
                location = preferences.preferred_location
                
            self._update_job_status(
                job_id,
                JobStatus.ANALYZING,
                10,
                "Analyzing global trends..."
            )
            
            trending_products = await self.trend_analyst.analyze_trends(
                query=query,
                region=region,
                limit=3
            )
            
            logger.info(f"Found {len(trending_products)} trending products")
            
            if not trending_products:
                raise Exception("No trending products found")
                
            self._update_job_status(
                job_id,
                JobStatus.SEARCHING_SUPPLIERS,
                40,
                "Searching for suppliers in Indonesia..."
            )
            
            top_product = trending_products[0]
            suppliers = await self.supplier_scout.find_suppliers(
                product_name=top_product.name,
                location=location,
                min_rating=4.0,
                limit=5
            )
            
            logger.info(f"Found {len(suppliers)} suppliers")
            
            if not suppliers:
                raise Exception("No suppliers found")
                
            outreach_results = []
            
            if auto_contact and suppliers:
                self._update_job_status(
                    job_id,
                    JobStatus.CONTACTING,
                    70,
                    "Contacting suppliers..."
                )
                
                outreach_results = await self.outreach_agent.contact_suppliers(
                    product_name=top_product.name,
                    quantity=quantity,
                    suppliers=suppliers,
                    channels=["whatsapp", "email"]
                )
                
                logger.info(f"Contacted {len(outreach_results)} suppliers")
                
            self._update_job_status(
                job_id,
                JobStatus.COMPLETED,
                90,
                "Generating final report..."
            )
            
            analysis_summary = await self.trend_analyst.generate_analysis_summary(
                trending_products
            )
            
            supplier_summary = await self.supplier_scout.generate_search_summary(
                suppliers
            )
            
            final_summary = self._generate_final_summary(
                trending_products,
                suppliers,
                outreach_results
            )
            
            recommendations = self._generate_recommendations(
                trending_products,
                suppliers
            )
            
            next_steps = self._generate_next_steps(
                suppliers,
                auto_contact
            )
            
            report = FinalReport(
                job_id=job_id,
                user_id=user_id,
                query=query,
                trending_products=trending_products,
                suppliers=suppliers,
                outreach_results=outreach_results,
                summary=final_summary,
                recommendations=recommendations,
                next_steps=next_steps,
                created_at=datetime.now(),
                marketing_campaign_ready=True
            )
            
            await self.memory_keeper.save_interaction(user_id, report)
            
            self._update_job_status(
                job_id,
                JobStatus.COMPLETED,
                100,
                "Workflow completed successfully!",
                result=report.model_dump()
            )
            
            logger.info(f"Workflow {job_id} completed successfully")
            
            return report
            
        except Exception as e:
            logger.error(f"Workflow {job_id} failed: {str(e)}")
            
            self._update_job_status(
                job_id,
                JobStatus.FAILED,
                0,
                f"Workflow failed: {str(e)}"
            )
            
            raise
            
    def _update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: int,
        message: str,
        result: Optional[Dict[str, Any]] = None
    ):
        """Update job status"""
        self.jobs[job_id] = {
            "status": status,
            "progress": progress,
            "message": message,
            "result": result,
            "updated_at": datetime.now()
        }
        
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status"""
        return self.jobs.get(job_id)
        
    def _generate_final_summary(
        self,
        products,
        suppliers,
        outreach_results
    ) -> str:
        """Generate final summary"""
        
        summary = f"""
## 🎯 TrendScout Analysis Complete!

### 📊 Trending Products Found: {len(products)}

Top Product: **{products[0].name}**
- Trend Score: {products[0].trend_score:.1f}/100
- Growth: +{products[0].growth_percentage:.1f}%
- Platform: {products[0].platform}
- Search Volume: {products[0].search_volume:,}

### 🏪 Suppliers Found: {len(suppliers)}

Top suppliers are located in:
{', '.join(set(s.city for s in suppliers[:3]))}

Average Rating: {sum(s.rating for s in suppliers) / len(suppliers):.1f}/5.0

### 📧 Outreach Status

{len([m for m in outreach_results if m.status == 'sent'])} messages sent successfully
{len([m for m in outreach_results if m.status == 'failed'])} messages failed

---

✅ **Ready to Start Marketing Campaign!**
"""
        
        return summary
        
    def _generate_recommendations(self, products, suppliers) -> list:
        """Generate recommendations"""
        
        recommendations = [
            f"Focus on {products[0].name} - highest trend score",
            f"Contact suppliers in {suppliers[0].city} first - best ratings",
            f"Negotiate bulk pricing for {20} pcs or more",
            "Start with small test order to verify quality",
            "Launch Instagram campaign to capitalize on trend"
        ]
        
        return recommendations
        
    def _generate_next_steps(self, suppliers, auto_contact) -> list:
        """Generate next steps"""
        
        steps = []
        
        if auto_contact:
            steps.append("✅ Wait for supplier responses (24-48 hours)")
            steps.append("Compare quotes and select best supplier")
        else:
            steps.append("Contact suppliers manually")
            steps.append("Request quotations")
            
        steps.extend([
            "Place test order (10-20 pcs)",
            "Launch marketing campaign",
            "Monitor sales and reorder"
        ])
        
        return steps
        
    async def interpret_query(self, query: str) -> Dict[str, Any]:
        """Interpret user query to extract intent and parameters"""
        
        query_lower = query.lower()
        
        intent = {
            "product_category": None,
            "region": "global",
            "action": "analyze",
            "quantity": 20
        }
        
        if any(word in query_lower for word in ['europe', 'eropa', 'eu']):
            intent["region"] = "europe"
        elif any(word in query_lower for word in ['us', 'america', 'amerika']):
            intent["region"] = "US"
        elif any(word in query_lower for word in ['asia']):
            intent["region"] = "asia"
            
        if any(word in query_lower for word in ['contact', 'hubungi', 'message']):
            intent["action"] = "contact"
            
        return intent
