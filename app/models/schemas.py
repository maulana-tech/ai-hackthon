from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    SCRAPING = "scraping"
    ANALYZING = "analyzing"
    SEARCHING_SUPPLIERS = "searching_suppliers"
    CONTACTING = "contacting"
    COMPLETED = "completed"
    FAILED = "failed"

class TrendingProduct(BaseModel):
    name: str
    category: str
    trend_score: float
    growth_percentage: float
    search_volume: int
    region: str
    platform: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    price_range: Optional[str] = None
    keywords: List[str] = []
    # Extended fields for bestseller analysis
    rating: Optional[float] = None
    total_sold: Optional[int] = None
    review_count: Optional[int] = None
    shop_name: Optional[str] = None
    shop_location: Optional[str] = None
    product_url: Optional[str] = None
    is_official: bool = False
    
class Supplier(BaseModel):
    name: str
    store_name: str
    rating: float = 4.0
    location: str = "Indonesia"
    city: Optional[str] = None
    product_name: str = "Unknown Product"
    price: float = 0
    currency: str = "IDR"
    stock_available: bool = True
    minimum_order: int = 1
    url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    marketplace: str = "Unknown"
    response_rate: Optional[float] = None
    verified: bool = False
    is_bestseller: bool = False
    total_sold: Optional[int] = None
    review_count: Optional[int] = None
    
class OutreachMessage(BaseModel):
    supplier_id: str
    supplier_name: str
    channel: str
    message: str
    status: str
    sent_at: datetime
    response: Optional[str] = None
    
class UserPreference(BaseModel):
    user_id: str
    niche: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_location: Optional[str] = None
    preferred_marketplace: Optional[List[str]] = []
    language: str = "id"
    
class TrendAnalysisRequest(BaseModel):
    query: str
    user_id: str
    region: str = "global"
    category: Optional[str] = None
    limit: int = Field(default=3, ge=1, le=10)
    
class SupplierSearchRequest(BaseModel):
    product_name: str
    user_id: str
    location: Optional[str] = None
    min_rating: float = 4.0
    limit: int = Field(default=5, ge=1, le=20)
    
class OutreachRequest(BaseModel):
    product_name: str
    quantity: int
    suppliers: List[Supplier]
    message_template: Optional[str] = None
    channels: List[str] = ["whatsapp", "email"]
    
class CampaignRequest(BaseModel):
    product: TrendingProduct
    target_audience: str
    budget: float
    platforms: List[str] = ["instagram", "tiktok"]
    duration_days: int = 7
    
class TrendAnalysisResponse(BaseModel):
    job_id: str
    status: JobStatus
    trending_products: List[TrendingProduct]
    analysis_summary: str
    created_at: datetime
    
class SupplierSearchResponse(BaseModel):
    job_id: str
    status: JobStatus
    suppliers: List[Supplier]
    search_summary: str
    created_at: datetime
    
class OutreachResponse(BaseModel):
    job_id: str
    status: JobStatus
    messages: List[OutreachMessage]
    success_count: int
    failed_count: int
    created_at: datetime
    
class FinalReport(BaseModel):
    job_id: str
    user_id: str
    query: str
    trending_products: List[TrendingProduct]
    suppliers: List[Supplier]
    outreach_results: List[OutreachMessage]
    summary: str
    recommendations: List[str]
    next_steps: List[str]
    created_at: datetime
    marketing_campaign_ready: bool = False
    
class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int
    message: str
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
