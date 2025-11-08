from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging

from app.models.schemas import (
    TrendAnalysisRequest,
    SupplierSearchRequest,
    OutreachRequest,
    FinalReport,
    JobStatusResponse
)
from app.agents.super_agent import SuperAgent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/agent", tags=["agent"])

super_agent = SuperAgent()

@router.post("/analyze-trend", response_model=Dict[str, Any])
async def analyze_trend(request: TrendAnalysisRequest):
    """
    Analyze trending products for a query
    """
    try:
        logger.info(f"Analyzing trends for: {request.query}")
        
        trending_products = await super_agent.trend_analyst.analyze_trends(
            query=request.query,
            region=request.region,
            limit=request.limit
        )
        
        summary = await super_agent.trend_analyst.generate_analysis_summary(
            trending_products
        )
        
        return {
            "success": True,
            "data": {
                "products": [p.model_dump() for p in trending_products],
                "summary": summary
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find-suppliers", response_model=Dict[str, Any])
async def find_suppliers(request: SupplierSearchRequest):
    """
    Find suppliers for a product
    """
    try:
        logger.info(f"Finding suppliers for: {request.product_name}")
        
        suppliers = await super_agent.supplier_scout.find_suppliers(
            product_name=request.product_name,
            location=request.location,
            min_rating=request.min_rating,
            limit=request.limit
        )
        
        summary = await super_agent.supplier_scout.generate_search_summary(
            suppliers
        )
        
        return {
            "success": True,
            "data": {
                "suppliers": [s.model_dump() for s in suppliers],
                "summary": summary
            }
        }
        
    except Exception as e:
        logger.error(f"Error finding suppliers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contact-suppliers", response_model=Dict[str, Any])
async def contact_suppliers(request: OutreachRequest):
    """
    Contact suppliers via WhatsApp/Email
    """
    try:
        logger.info(f"Contacting {len(request.suppliers)} suppliers")
        
        messages = await super_agent.outreach_agent.contact_suppliers(
            product_name=request.product_name,
            quantity=request.quantity,
            suppliers=request.suppliers,
            channels=request.channels
        )
        
        summary = await super_agent.outreach_agent.generate_outreach_summary(
            messages
        )
        
        return {
            "success": True,
            "data": summary
        }
        
    except Exception as e:
        logger.error(f"Error contacting suppliers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-workflow", response_model=Dict[str, Any])
async def execute_workflow(
    query: str,
    user_id: str,
    quantity: int = 20,
    region: str = "global",
    location: str = None,
    auto_contact: bool = True,
    background_tasks: BackgroundTasks = None
):
    """
    Execute complete workflow with intent classification
    This is the main endpoint that routes to appropriate agent based on intent
    """
    try:
        logger.info(f"Executing workflow for query: {query}")
        
        # Use the new execute method which does intent classification
        result = await super_agent.execute(
            query=query,
            user_id=user_id,
            quantity=quantity,
            region=region,
            location=location,
            auto_contact=auto_contact
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get status of a job
    """
    try:
        status = super_agent.get_job_status(job_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
            
        return JobStatusResponse(
            job_id=job_id,
            status=status["status"],
            progress=status["progress"],
            message=status["message"],
            result=status.get("result"),
            created_at=status.get("created_at"),
            updated_at=status.get("updated_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/launch-campaign", response_model=Dict[str, Any])
async def launch_campaign(
    product_name: str,
    user_id: str,
    platform: str = "instagram",
    budget: float = 500000
):
    """
    Launch marketing campaign for a product
    (Part B - Marketing Swarm)
    """
    try:
        logger.info(f"Launching campaign for: {product_name}")
        
        return {
            "success": True,
            "message": "Marketing campaign feature coming soon!",
            "data": {
                "product": product_name,
                "platform": platform,
                "budget": budget,
                "status": "Campaign setup in progress"
            }
        }
        
    except Exception as e:
        logger.error(f"Error launching campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/history")
async def get_user_history(user_id: str, limit: int = 10):
    """
    Get user interaction history
    """
    try:
        history = await super_agent.memory_keeper.get_history(user_id, limit)
        
        return {
            "success": True,
            "data": history
        }
        
    except Exception as e:
        logger.error(f"Error getting user history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/insights")
async def get_user_insights(user_id: str):
    """
    Get user behavior insights
    """
    try:
        insights = await super_agent.memory_keeper.get_user_insights(user_id)
        
        return {
            "success": True,
            "data": insights
        }
        
    except Exception as e:
        logger.error(f"Error getting user insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/indonetwork/search")
async def search_indonetwork(
    product_name: str,
    min_rating: float = 4.0
):
    """
    Search Indonetwork.co.id for B2B suppliers with contact details
    """
    try:
        logger.info(f"Searching Indonetwork for: {product_name}")
        
        suppliers = await super_agent.supplier_scout._search_indonetwork(
            product_name,
            min_rating
        )
        
        return {
            "success": True,
            "data": {
                "suppliers": [s.model_dump() for s in suppliers],
                "count": len(suppliers)
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching Indonetwork: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/indonetwork/batch-scrape")
async def batch_scrape_companies(company_urls: list[str]):
    """
    Batch scrape multiple company URLs from Indonetwork
    """
    try:
        logger.info(f"Batch scraping {len(company_urls)} companies")
        
        companies = await super_agent.supplier_scout.batch_scrape_companies(
            company_urls
        )
        
        return {
            "success": True,
            "data": {
                "companies": companies,
                "count": len(companies)
            }
        }
        
    except Exception as e:
        logger.error(f"Error batch scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indonetwork/company-details")
async def get_company_details(company_url: str):
    """
    Get detailed company information from Indonetwork
    """
    try:
        logger.info(f"Getting company details: {company_url}")
        
        details = await super_agent.supplier_scout._get_indonetwork_company_details(
            company_url
        )
        
        return {
            "success": True,
            "data": details
        }
        
    except Exception as e:
        logger.error(f"Error getting company details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indonetwork/category/{category}")
async def search_by_category(category: str, limit: int = 10):
    """
    Search Indonetwork by product category
    """
    try:
        logger.info(f"Searching category: {category}")
        
        suppliers = await super_agent.supplier_scout.search_indonetwork_by_category(
            category,
            limit
        )
        
        return {
            "success": True,
            "data": {
                "suppliers": [s.model_dump() for s in suppliers],
                "count": len(suppliers)
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indonetwork/export-markdown")
async def export_supplier_markdown(company_url: str):
    """
    Get supplier info in markdown format
    """
    try:
        logger.info(f"Exporting to markdown: {company_url}")
        
        result = await super_agent.supplier_scout.get_indonetwork_supplier_with_markdown(
            company_url
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error exporting markdown: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
