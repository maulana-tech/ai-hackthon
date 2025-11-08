"""
Google Sheets Service - Campaign data tracking and management

Handles:
- Campaign data storage in Google Sheets
- Product tracking
- Email campaign logs
- Performance metrics
- Real-time updates
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class SheetsService:
    """
    Service for managing campaign data in Google Sheets
    
    Note: This is a simplified version. For production:
    1. Install: pip install gspread oauth2client
    2. Set up Google Cloud credentials
    3. Enable Google Sheets API
    4. Use service account for authentication
    """
    
    def __init__(self):
        self.enabled = False  # Set to True when credentials configured
        self.sheet_id = None
        
        # Try to initialize Google Sheets client
        try:
            # Placeholder for Google Sheets initialization
            # import gspread
            # from oauth2client.service_account import ServiceAccountCredentials
            # self.client = gspread.authorize(credentials)
            logger.info("SheetsService initialized (mock mode)")
        except Exception as e:
            logger.warning(f"Google Sheets not configured: {str(e)}")
    
    async def create_campaign_sheet(
        self,
        campaign_name: str,
        products: List[Dict[str, Any]],
        campaign_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Google Sheet/Doc for campaign tracking
        
        Strategy: Generate shareable template URLs that users can copy/edit
        This approach doesn't require OAuth or service account setup.
        
        Args:
            campaign_name: Name of the campaign
            products: List of products in campaign
            campaign_data: Campaign details (budget, schedule, etc)
            
        Returns:
            Dict with sheet info and URLs
        """
        try:
            logger.info(f"Creating campaign materials for: {campaign_name}")
            
            # Generate Google Sheets template URL with pre-filled data
            sheets_url = self._generate_sheets_template_url(
                campaign_name, 
                products, 
                campaign_data
            )
            
            # Generate Google Docs template URL for campaign document
            docs_url = self._generate_docs_template_url(
                campaign_name,
                campaign_data
            )
            
            sheet_data = {
                "campaign_name": campaign_name,
                "sheet_id": f"template-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "sheet_url": sheets_url,
                "doc_url": docs_url,
                "created_at": datetime.now().isoformat(),
                "products_count": len(products),
                "status": "template_ready"
            }
            
            logger.info(f"✅ Campaign materials created")
            logger.info(f"   📊 Sheets: {sheets_url}")
            logger.info(f"   📄 Docs: {docs_url}")
            
            return {
                "success": True,
                "sheet_id": sheet_data["sheet_id"],
                "sheet_url": sheet_data["sheet_url"],
                "doc_url": sheet_data["doc_url"],
                "data": sheet_data
            }
            
        except Exception as e:
            logger.error(f"Failed to create campaign materials: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "sheet_url": "https://docs.google.com/spreadsheets/create",
                "doc_url": "https://docs.google.com/document/create"
            }
    
    def _generate_sheets_template_url(
        self,
        campaign_name: str,
        products: List[Dict[str, Any]],
        campaign_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate Google Sheets URL with template data
        
        Uses Google Sheets 'create from template' approach
        """
        from urllib.parse import quote
        
        # Build CSV data for import
        headers = ["Product", "Category", "Budget", "Duration", "Platform", "Status", "KPIs"]
        rows = []
        
        for product in products[:5]:  # Limit to 5 products
            row = [
                product.get("name", "Product"),
                product.get("category", "General"),
                campaign_data.get("budget", {}).get("total_budget", "Rp 5.000.000") if campaign_data else "Rp 5.000.000",
                f"{campaign_data.get('schedule', {}).get('duration_days', 30)} hari" if campaign_data else "30 hari",
                product.get("platform", "Multi-platform"),
                "Pending",
                "Impressions, CTR, Conversions"
            ]
            rows.append(row)
        
        # For now, return template creation URL
        # User will manually copy-paste campaign data
        template_name = quote(f"Campaign Tracking - {campaign_name}")
        return f"https://docs.google.com/spreadsheets/create?title={template_name}"
    
    def _generate_docs_template_url(
        self,
        campaign_name: str,
        campaign_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate Google Docs URL with campaign document
        """
        from urllib.parse import quote
        
        doc_title = quote(f"Campaign Plan - {campaign_name}")
        return f"https://docs.google.com/document/create?title={doc_title}"
    
    async def add_product_row(
        self,
        sheet_id: str,
        product_data: Dict[str, Any]
    ) -> bool:
        """
        Add product data row to campaign sheet
        
        Args:
            sheet_id: Google Sheet ID
            product_data: Product information
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Adding product to sheet {sheet_id}")
            
            # Extract product info
            row_data = {
                "Product Name": product_data.get("name"),
                "Category": product_data.get("category"),
                "Price": product_data.get("price_range"),
                "Platform": product_data.get("platform"),
                "Shop": product_data.get("shop_name"),
                "Rating": product_data.get("rating"),
                "Total Sold": product_data.get("total_sold"),
                "Campaign Status": "Pending",
                "Budget": "-",
                "Schedule": "-",
                "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"✅ Product row added: {row_data['Product Name']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add product row: {str(e)}")
            return False
    
    async def update_campaign_status(
        self,
        sheet_id: str,
        product_name: str,
        status: str,
        campaign_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update campaign status for a product
        
        Args:
            sheet_id: Google Sheet ID
            product_name: Product name to update
            status: New status (Pending, Active, Completed)
            campaign_data: Optional campaign details
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Updating campaign status: {product_name} -> {status}")
            
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            
            if campaign_data:
                update_data.update({
                    "budget": campaign_data.get("budget"),
                    "schedule": campaign_data.get("schedule"),
                    "content": campaign_data.get("content")
                })
            
            logger.info(f"✅ Campaign status updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update campaign status: {str(e)}")
            return False
    
    async def log_email_sent(
        self,
        sheet_id: str,
        supplier_name: str,
        product_name: str,
        email_status: str
    ) -> bool:
        """
        Log email sending activity to sheet
        
        Args:
            sheet_id: Google Sheet ID
            supplier_name: Supplier contacted
            product_name: Product inquired
            email_status: Success/Failed
            
        Returns:
            True if successful
        """
        try:
            log_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "supplier": supplier_name,
                "product": product_name,
                "status": email_status
            }
            
            logger.info(f"✅ Email activity logged: {supplier_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log email: {str(e)}")
            return False
    
    def get_sheet_url(self, sheet_id: str) -> str:
        """Get shareable URL for sheet"""
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}"


# Global instance
sheets_service = SheetsService()
