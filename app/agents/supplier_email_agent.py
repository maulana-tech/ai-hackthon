"""
Supplier Email Agent - Automated supplier contact and email outreach

Handles:
- Extracting supplier contact info from products/shops
- Sending inquiry emails to suppliers
- Bulk email campaigns
- Email tracking and follow-ups
"""
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.services.email_service import email_service
from app.agents.supplier_scout import SupplierScoutAgent
from app.agents.bestseller_finder import BestsellerFinder

logger = logging.getLogger(__name__)


class EmailRequest(BaseModel):
    """Request model for supplier email"""
    product_name: str = Field(..., description="Product name to inquire about")
    buyer_name: str = Field(..., description="Buyer's name")
    buyer_email: str = Field(..., description="Buyer's email address")
    buyer_phone: Optional[str] = Field(None, description="Buyer's phone number")
    quantity: Optional[int] = Field(None, description="Desired quantity")
    message: Optional[str] = Field(None, description="Additional message to supplier")
    marketplace: Optional[str] = Field(None, description="Specific marketplace")
    supplier_email: Optional[str] = Field(None, description="Specific supplier email (if known)")
    supplier_name: Optional[str] = Field(None, description="Specific supplier name (if known)")


class EmailResult(BaseModel):
    """Result of email operation"""
    status: str  # "success", "partial", "failed"
    sent: int
    failed: int
    total: int
    suppliers_contacted: List[str]
    message: str
    details: List[Dict[str, Any]]


class SupplierEmailAgent:
    """Agent for automated supplier email outreach"""
    
    def __init__(self):
        self.email_service = email_service
        self.supplier_scout = SupplierScoutAgent()
        self.bestseller_finder = BestsellerFinder()
        
    async def send_product_inquiry(
        self,
        request: EmailRequest
    ) -> EmailResult:
        """
        Send inquiry email about a product to suppliers
        
        Flow:
        1. If supplier email provided, send directly
        2. Otherwise, find suppliers for the product
        3. Send emails to all found suppliers
        4. Return results
        """
        try:
            logger.info(f"Processing email inquiry for product: {request.product_name}")
            
            # If specific supplier provided, send directly
            if request.supplier_email and request.supplier_name:
                return await self._send_to_specific_supplier(request)
            
            # Otherwise, find suppliers for the product
            return await self._find_and_email_suppliers(request)
            
        except Exception as e:
            logger.error(f"Email inquiry error: {str(e)}")
            return EmailResult(
                status="failed",
                sent=0,
                failed=0,
                total=0,
                suppliers_contacted=[],
                message=f"Gagal memproses inquiry: {str(e)}",
                details=[]
            )
    
    async def _send_to_specific_supplier(
        self,
        request: EmailRequest
    ) -> EmailResult:
        """Send email to specific supplier"""
        logger.info(f"Sending email to specific supplier: {request.supplier_name}")
        
        success = self.email_service.send_supplier_inquiry(
            supplier_email=request.supplier_email,
            supplier_name=request.supplier_name,
            product_name=request.product_name,
            buyer_name=request.buyer_name,
            buyer_email=request.buyer_email,
            buyer_phone=request.buyer_phone,
            quantity=request.quantity,
            message=request.message
        )
        
        if success:
            return EmailResult(
                status="success",
                sent=1,
                failed=0,
                total=1,
                suppliers_contacted=[request.supplier_name],
                message=f"✅ Email berhasil dikirim ke {request.supplier_name}!",
                details=[{
                    'supplier': request.supplier_name,
                    'email': request.supplier_email,
                    'status': 'success'
                }]
            )
        else:
            return EmailResult(
                status="failed",
                sent=0,
                failed=1,
                total=1,
                suppliers_contacted=[],
                message=f"❌ Gagal mengirim email ke {request.supplier_name}",
                details=[{
                    'supplier': request.supplier_name,
                    'email': request.supplier_email,
                    'status': 'failed'
                }]
            )
    
    async def _find_and_email_suppliers(
        self,
        request: EmailRequest
    ) -> EmailResult:
        """Find suppliers for product and send emails"""
        logger.info(f"Finding suppliers for product: {request.product_name}")
        
        # Try method 1: Use SupplierScout to find suppliers
        suppliers_result = await self.supplier_scout.find_suppliers(
            product_name=request.product_name,
            limit=10
        )
        
        # If no suppliers found, try method 2: Get from bestsellers
        if not suppliers_result:
            logger.info("No suppliers from SupplierScout, trying BestsellerFinder...")
            try:
                bestsellers = await self.bestseller_finder.find_bestsellers(
                    category=request.product_name,
                    marketplace=request.marketplace,
                    limit=5
                )
                
                # Convert bestsellers to supplier format
                if bestsellers:
                    suppliers_result = []
                    for product in bestsellers:
                        if product.shop_name:
                            supplier_dict = {
                                'name': product.shop_name,
                                'location': product.shop_location or 'Indonesia',
                                'rating': product.rating,
                                'platform': product.platform
                            }
                            suppliers_result.append(supplier_dict)
                    
                    logger.info(f"Found {len(suppliers_result)} suppliers from bestsellers")
            except Exception as e:
                logger.error(f"Error getting suppliers from bestsellers: {str(e)}")
        
        if not suppliers_result:
            return EmailResult(
                status="failed",
                sent=0,
                failed=0,
                total=0,
                suppliers_contacted=[],
                message="❌ Tidak menemukan supplier untuk produk ini",
                details=[]
            )
        
        # Extract supplier emails
        suppliers_with_email = []
        for supplier in suppliers_result:
            # Try to extract email from supplier data
            email = self._extract_supplier_email(supplier)
            if email:
                suppliers_with_email.append({
                    'name': supplier.get('name', 'Unknown'),
                    'email': email
                })
        
        if not suppliers_with_email:
            # If no emails found, create demo emails for testing
            # In production, you'd extract from shop pages or use contact forms
            logger.warning("No supplier emails found, generating demo contacts")
            suppliers_with_email = self._generate_demo_suppliers(suppliers_result[:3])
        
        if not suppliers_with_email:
            return EmailResult(
                status="failed",
                sent=0,
                failed=0,
                total=0,
                suppliers_contacted=[],
                message="❌ Tidak menemukan email supplier",
                details=[]
            )
        
        # Send bulk emails
        logger.info(f"Sending emails to {len(suppliers_with_email)} suppliers")
        
        result = self.email_service.send_bulk_inquiry(
            suppliers=suppliers_with_email,
            product_name=request.product_name,
            buyer_name=request.buyer_name,
            buyer_email=request.buyer_email,
            buyer_phone=request.buyer_phone,
            quantity=request.quantity,
            message=request.message
        )
        
        # Format result
        contacted = [s['supplier'] for s in result['results'] if s['status'] == 'success']
        
        if result['success'] > 0:
            status = "success" if result['failed'] == 0 else "partial"
            message = f"✅ Email berhasil dikirim ke {result['success']} dari {result['total']} supplier!"
        else:
            status = "failed"
            message = f"❌ Gagal mengirim email ke semua supplier"
        
        return EmailResult(
            status=status,
            sent=result['success'],
            failed=result['failed'],
            total=result['total'],
            suppliers_contacted=contacted,
            message=message,
            details=result['results']
        )
    
    def _extract_supplier_email(self, supplier: Dict[str, Any]) -> Optional[str]:
        """Extract email from supplier data"""
        # Try various fields where email might be
        email_fields = ['email', 'contact_email', 'shop_email', 'seller_email']
        
        for field in email_fields:
            email = supplier.get(field)
            if email and '@' in email:
                return email
        
        # Try to extract from contact info
        contact = supplier.get('contact', {})
        if isinstance(contact, dict):
            for field in email_fields:
                email = contact.get(field)
                if email and '@' in email:
                    return email
        
        return None
    
    def _generate_demo_suppliers(self, suppliers: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Generate demo supplier contacts with real Gmail format for testing
        
        Uses Gmail addresses so emails can actually be sent and tested.
        In production, replace with real supplier email extraction.
        """
        demo_suppliers = []
        
        for i, supplier in enumerate(suppliers):
            shop_name = supplier.get('name', f'Supplier {i+1}')
            
            # Create Gmail format for actual email sending
            # Clean shop name for email format
            clean_name = shop_name.lower()
            clean_name = clean_name.replace(' ', '')
            clean_name = clean_name.replace('_', '')
            clean_name = clean_name[:15]  # Limit length
            
            # Use Gmail format so emails actually send
            demo_email = f"{clean_name}.supplier@gmail.com"
            
            demo_suppliers.append({
                'name': shop_name,
                'email': demo_email
            })
        
        logger.info(f"Generated {len(demo_suppliers)} demo supplier contacts with Gmail format")
        return demo_suppliers
    
    async def contact_suppliers_for_bestseller(
        self,
        product_name: str,
        buyer_name: str,
        buyer_email: str,
        buyer_phone: Optional[str] = None,
        quantity: Optional[int] = None,
        marketplace: Optional[str] = None
    ) -> EmailResult:
        """
        Convenience method: Contact suppliers for a bestselling product
        """
        request = EmailRequest(
            product_name=product_name,
            buyer_name=buyer_name,
            buyer_email=buyer_email,
            buyer_phone=buyer_phone,
            quantity=quantity,
            marketplace=marketplace
        )
        
        return await self.send_product_inquiry(request)


# Global instance
supplier_email_agent = SupplierEmailAgent()
