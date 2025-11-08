import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from app.models.schemas import (
    TrendAnalysisRequest,
    SupplierSearchRequest,
    OutreachRequest,
    FinalReport,
    JobStatus,
    TrendingProduct,
    Supplier
)
from app.agents.intent_classifier import IntentClassifier
from app.agents.trend_analyst import TrendAnalystAgent
from app.agents.supplier_scout import SupplierScoutAgent
from app.agents.outreach_agent import OutreachAgent
from app.agents.memory_keeper import MemoryKeeperAgent
from app.agents.bestseller_finder import BestsellerFinder
from app.integrations.getcirclo_client import GetCircloClient
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class SuperAgent:
    """
    Super Agent - Orchestrator that coordinates all sub-agents
    
    Enhanced with:
    - Intent classification
    - User context management
    - Flexible workflow routing
    - Progress tracking
    - Memory integration
    """
    
    def __init__(self):
        self.name = "TrendScout Super Agent"
        self.intent_classifier = IntentClassifier()
        self.trend_analyst = TrendAnalystAgent()
        self.supplier_scout = SupplierScoutAgent()
        self.outreach_agent = OutreachAgent()
        self.memory_keeper = MemoryKeeperAgent()
        self.bestseller_finder = BestsellerFinder()
        self.circlo = GetCircloClient()
        self.jobs = {}
        
    async def execute(
        self,
        query: str,
        user_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Main entry point - Classify intent and route to appropriate workflow
        
        Args:
            query: Natural language query from user
            user_id: User identifier
            **kwargs: Additional parameters
            
        Returns:
            Result dict with job_id, status, and data
        """
        job_id = str(uuid.uuid4())
        
        logger.info(f"[{job_id}] New query from {user_id}: {query}")
        
        try:
            # Step 1: Get user context
            context = await self._get_user_context(user_id)
            
            # Step 2: Classify intent
            intent_result = await self.intent_classifier.classify(query, context)
            intent = intent_result['intent']
            params = intent_result['parameters']
            
            logger.info(f"[{job_id}] Intent: {intent}, Confidence: {intent_result['confidence']}")
            
            # Step 3: Route to appropriate workflow
            if intent == "find_trending_products":
                result = await self.workflow_find_trends(job_id, query, params)
                
            elif intent == "find_suppliers":
                result = await self.workflow_find_suppliers(job_id, query, params)
                
            elif intent == "find_trending_suppliers":
                result = await self.workflow_trending_suppliers(job_id, query, user_id, params)
            
            elif intent == "find_bestsellers":
                result = await self.workflow_find_bestsellers(job_id, query, user_id, params)
                
            elif intent == "contact_suppliers":
                result = await self.workflow_contact_suppliers(job_id, user_id, params)
                
            elif intent == "get_status":
                result = await self.workflow_get_status(job_id, user_id, params)
                
            else:
                result = {
                    "job_id": job_id,
                    "status": "completed",
                    "message": "Intent not yet implemented",
                    "intent": intent
                }
            
            # Step 4: Save to memory
            await self.memory_keeper.save_interaction(user_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"[{job_id}] Workflow error: {str(e)}", exc_info=True)
            return {
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context from memory"""
        try:
            preferences = await self.memory_keeper.get_preference(user_id)
            history = await self.memory_keeper.get_history(user_id, limit=5)
            
            return {
                "user_id": user_id,
                "preferences": preferences.model_dump() if preferences else {},
                "history": history
            }
        except Exception as e:
            logger.warning(f"Could not get user context: {str(e)}")
            return {"user_id": user_id, "preferences": {}, "history": []}
    
    async def workflow_find_trends(
        self,
        job_id: str,
        query: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Workflow: Find trending products only"""
        logger.info(f"[{job_id}] Executing: Find Trends")
        
        self._update_job_status(job_id, JobStatus.ANALYZING, 10, "Analyzing trends...")
        
        category = params.get("product_category") or params.get("product_name") or query
        
        trends = await self.trend_analyst.analyze_trends(
            query=category,
            region=params.get("region", "global"),
            limit=params.get("limit", 5)
        )
        
        self._update_job_status(job_id, JobStatus.COMPLETED, 100, "Trends analysis complete")
        
        return {
            "job_id": job_id,
            "status": "completed",
            "intent": "find_trending_products",
            "query": query,
            "results": {
                "trending_products": [p.model_dump() for p in trends],
                "count": len(trends)
            }
        }
    
    async def workflow_find_suppliers(
        self,
        job_id: str,
        query: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Workflow: Find suppliers only"""
        logger.info(f"[{job_id}] Executing: Find Suppliers")
        
        self._update_job_status(job_id, JobStatus.SEARCHING_SUPPLIERS, 20, "Searching suppliers...")
        
        product = params.get("product_name") or params.get("product_category") or query
        
        suppliers = await self.supplier_scout.find_suppliers(
            product_name=product,
            location=params.get("location"),
            min_rating=params.get("min_rating", 4.0),
            limit=params.get("limit", 5)
        )
        
        self._update_job_status(job_id, JobStatus.COMPLETED, 100, f"Found {len(suppliers)} suppliers")
        
        return {
            "job_id": job_id,
            "status": "completed",
            "intent": "find_suppliers",
            "query": query,
            "results": {
                "product": product,
                "suppliers": [s.model_dump() for s in suppliers],
                "count": len(suppliers)
            }
        }
    
    async def workflow_trending_suppliers(
        self,
        job_id: str,
        query: str,
        user_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Workflow: Find trending products AND suppliers (Full pipeline)"""
        logger.info(f"[{job_id}] Executing: Trending + Suppliers (Full Pipeline)")
        
        # Step 1: Find trends
        self._update_job_status(job_id, JobStatus.ANALYZING, 10, "Analyzing trends...")
        
        category = params.get("product_category") or params.get("product_name") or query
        
        trends = await self.trend_analyst.analyze_trends(
            query=category,
            region=params.get("region", "global"),
            limit=3
        )
        
        if not trends:
            return {
                "job_id": job_id,
                "status": "completed",
                "message": "No trending products found",
                "results": {"trending_products": [], "suppliers": []}
            }
        
        # Step 2: Find suppliers for top trending product
        self._update_job_status(job_id, JobStatus.SEARCHING_SUPPLIERS, 40, "Finding suppliers...")
        
        top_product = trends[0]
        suppliers = await self.supplier_scout.find_suppliers(
            product_name=top_product.name,
            location=params.get("location"),
            min_rating=params.get("min_rating", 4.0),
            limit=params.get("limit", 5)
        )
        
        # Step 3: Optional contact suppliers
        messages = []
        if params.get("auto_contact") and suppliers:
            self._update_job_status(job_id, JobStatus.CONTACTING, 70, "Contacting suppliers...")
            
            messages = await self.outreach_agent.contact_suppliers(
                product_name=top_product.name,
                quantity=params.get("quantity", 20),
                suppliers=suppliers[:5]
            )
        
        # Step 4: Generate report
        self._update_job_status(job_id, JobStatus.COMPLETED, 100, "Workflow complete!")
        
        report = {
            "job_id": job_id,
            "status": "completed",
            "intent": "find_trending_suppliers",
            "query": query,
            "results": {
                "trending_products": [p.model_dump() for p in trends],
                "top_product": top_product.model_dump(),
                "suppliers": [s.model_dump() for s in suppliers],
                "outreach_messages": [m.model_dump() for m in messages] if messages else [],
                "summary": self._generate_summary(trends, suppliers, messages)
            }
        }
        
        return report
    
    async def workflow_find_bestsellers(
        self,
        job_id: str,
        query: str,
        user_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Workflow: Find bestselling products from marketplaces + auto-find suppliers
        
        This is the ADVANCED workflow that:
        1. Scrapes real marketplace data to find bestsellers
        2. Ranks by sales volume, rating, reviews
        3. Auto-finds suppliers for top products
        4. Returns actionable insights
        """
        logger.info(f"[{job_id}] Executing: Find Bestsellers (Advanced Discovery)")
        
        # Step 1: Find bestselling products from marketplaces
        self._update_job_status(job_id, JobStatus.ANALYZING, 10, "🔍 Discovering bestselling products...")
        
        category = params.get("product_category") or params.get("category")
        marketplace = params.get("marketplace")  # Can be None for all marketplaces
        limit = params.get("limit", 10)
        min_sold = params.get("min_sold", 100)  # Minimum units sold to qualify as bestseller
        
        bestsellers = await self.bestseller_finder.find_bestsellers(
            category=category,
            marketplace=marketplace,
            limit=limit,
            min_sold=min_sold,
            min_rating=params.get("min_rating", 4.0)
        )
        
        if not bestsellers:
            return {
                "job_id": job_id,
                "status": "completed",
                "message": "❌ No bestselling products found. Try adjusting your criteria.",
                "results": {
                    "bestsellers": [],
                    "suppliers": []
                }
            }
        
        # Step 2: Generate bestseller report
        self._update_job_status(job_id, JobStatus.ANALYZING, 40, f"📊 Analyzing {len(bestsellers)} products...")
        
        report = await self.bestseller_finder.generate_bestseller_report(bestsellers)
        
        # Step 3: Auto-find suppliers for top 3 bestselling products
        self._update_job_status(job_id, JobStatus.SEARCHING_SUPPLIERS, 60, "🏪 Finding suppliers...")
        
        suppliers_by_product = {}
        
        for i, product in enumerate(bestsellers[:3], 1):
            try:
                suppliers = await self.supplier_scout.find_suppliers(
                    product_name=product.name,
                    location=params.get("location"),
                    min_rating=4.0,
                    limit=3
                )
                
                if suppliers:
                    suppliers_by_product[product.name] = [s.model_dump() for s in suppliers]
                    logger.info(f"Found {len(suppliers)} suppliers for {product.name}")
                
            except Exception as e:
                logger.warning(f"Failed to find suppliers for {product.name}: {str(e)}")
        
        # Step 4: Complete
        self._update_job_status(job_id, JobStatus.COMPLETED, 100, "✅ Bestseller discovery complete")
        
        return {
            "job_id": job_id,
            "status": "completed",
            "intent": "find_bestsellers",
            "query": query,
            "results": {
                "bestsellers": [p.model_dump() for p in bestsellers],
                "count": len(bestsellers),
                "suppliers_by_product": suppliers_by_product,
                "report": report,
                "summary": {
                    "total_products": len(bestsellers),
                    "total_sold": sum(p.total_sold or 0 for p in bestsellers),
                    "avg_rating": round(sum(p.rating or 0 for p in bestsellers) / len(bestsellers), 2),
                    "official_stores": sum(1 for p in bestsellers if p.is_official),
                    "marketplaces": list(set(p.platform for p in bestsellers)),
                    "categories": list(set(p.category for p in bestsellers))
                }
            }
        }
    
    async def workflow_contact_suppliers(
        self,
        job_id: str,
        user_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Workflow: Contact previously found suppliers"""
        logger.info(f"[{job_id}] Executing: Contact Suppliers")
        
        # Get last search results from memory
        history = await self.memory_keeper.get_history(user_id, limit=1)
        
        if not history or not history[0].get("suppliers"):
            return {
                "job_id": job_id,
                "status": "completed",
                "message": "No previous suppliers found. Please search for suppliers first."
            }
        
        # Contact suppliers
        suppliers_data = history[0]["suppliers"]
        suppliers = [Supplier(**s) for s in suppliers_data[:5]]
        
        messages = await self.outreach_agent.contact_suppliers(
            product_name=params.get("product", "Product"),
            quantity=params.get("quantity", 20),
            suppliers=suppliers
        )
        
        return {
            "job_id": job_id,
            "status": "completed",
            "intent": "contact_suppliers",
            "results": {
                "suppliers_contacted": len(suppliers),
                "messages": [m.model_dump() for m in messages]
            }
        }
    
    async def workflow_get_status(
        self,
        job_id: str,
        user_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Workflow: Get status of previous job"""
        history = await self.memory_keeper.get_history(user_id, limit=1)
        
        if not history:
            return {
                "job_id": job_id,
                "status": "completed",
                "message": "No previous jobs found"
            }
        
        return {
            "job_id": job_id,
            "status": "completed",
            "results": history[0]
        }
    
    def _generate_summary(
        self,
        trends: List[TrendingProduct],
        suppliers: List[Supplier],
        messages: List[Any]
    ) -> str:
        """Generate human-readable summary"""
        summary = f"Found {len(trends)} trending products. "
        
        if trends:
            summary += f"Top trending: {trends[0].name} ({trends[0].trend_score:.1f} trend score). "
        
        summary += f"Located {len(suppliers)} suppliers in Indonesia. "
        
        if messages:
            summary += f"Contacted {len(messages)} suppliers via WhatsApp/Email."
        
        return summary
    
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
