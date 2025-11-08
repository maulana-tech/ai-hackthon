"""
Email Service - Automated email sending for supplier outreach

Handles:
- SMTP connection to Gmail
- Email template generation
- Supplier contact emails
- Order inquiry emails
- Follow-up emails
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailService:
    """Service for sending automated emails to suppliers"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        
    def _connect_smtp(self):
        """Establish SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            return server
        except Exception as e:
            logger.error(f"SMTP connection error: {str(e)}")
            raise
    
    def send_supplier_inquiry(
        self,
        supplier_email: str,
        supplier_name: str,
        product_name: str,
        buyer_name: str,
        buyer_email: str,
        buyer_phone: Optional[str] = None,
        quantity: Optional[int] = None,
        message: Optional[str] = None
    ) -> bool:
        """
        Send inquiry email to supplier
        
        Args:
            supplier_email: Supplier's email address
            supplier_name: Supplier/shop name
            product_name: Product being inquired about
            buyer_name: Buyer's name
            buyer_email: Buyer's email
            buyer_phone: Buyer's phone (optional)
            quantity: Desired quantity (optional)
            message: Additional message (optional)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            logger.info(f"Sending inquiry email to {supplier_email}")
            
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Inquiry: {product_name}"
            msg['From'] = self.from_email
            msg['To'] = supplier_email
            
            # Generate email body
            html_body = self._generate_inquiry_email_html(
                supplier_name=supplier_name,
                product_name=product_name,
                buyer_name=buyer_name,
                buyer_email=buyer_email,
                buyer_phone=buyer_phone,
                quantity=quantity,
                message=message
            )
            
            # Create plain text version
            text_body = self._generate_inquiry_email_text(
                supplier_name=supplier_name,
                product_name=product_name,
                buyer_name=buyer_name,
                buyer_email=buyer_email,
                buyer_phone=buyer_phone,
                quantity=quantity,
                message=message
            )
            
            # Attach both versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            server = self._connect_smtp()
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ Email sent successfully to {supplier_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {supplier_email}: {str(e)}")
            return False
    
    def send_bulk_inquiry(
        self,
        suppliers: List[Dict[str, Any]],
        product_name: str,
        buyer_name: str,
        buyer_email: str,
        buyer_phone: Optional[str] = None,
        quantity: Optional[int] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send inquiry to multiple suppliers
        
        Args:
            suppliers: List of supplier dicts with 'email' and 'name'
            product_name: Product name
            buyer_name: Buyer's name
            buyer_email: Buyer's email
            buyer_phone: Buyer's phone
            quantity: Desired quantity
            message: Additional message
            
        Returns:
            Dict with results: {success: int, failed: int, results: [...]}
        """
        results = []
        success_count = 0
        failed_count = 0
        
        for supplier in suppliers:
            supplier_email = supplier.get('email')
            supplier_name = supplier.get('name', 'Supplier')
            
            if not supplier_email:
                logger.warning(f"No email for supplier: {supplier_name}")
                failed_count += 1
                results.append({
                    'supplier': supplier_name,
                    'email': None,
                    'status': 'failed',
                    'reason': 'No email address'
                })
                continue
            
            success = self.send_supplier_inquiry(
                supplier_email=supplier_email,
                supplier_name=supplier_name,
                product_name=product_name,
                buyer_name=buyer_name,
                buyer_email=buyer_email,
                buyer_phone=buyer_phone,
                quantity=quantity,
                message=message
            )
            
            if success:
                success_count += 1
                results.append({
                    'supplier': supplier_name,
                    'email': supplier_email,
                    'status': 'success',
                    'sent_at': datetime.now().isoformat()
                })
            else:
                failed_count += 1
                results.append({
                    'supplier': supplier_name,
                    'email': supplier_email,
                    'status': 'failed',
                    'reason': 'SMTP error'
                })
        
        return {
            'success': success_count,
            'failed': failed_count,
            'total': len(suppliers),
            'results': results
        }
    
    def _generate_inquiry_email_html(
        self,
        supplier_name: str,
        product_name: str,
        buyer_name: str,
        buyer_email: str,
        buyer_phone: Optional[str],
        quantity: Optional[int],
        message: Optional[str]
    ) -> str:
        """Generate HTML email body for supplier inquiry"""
        
        quantity_text = f"<strong>Jumlah:</strong> {quantity} unit<br>" if quantity else ""
        phone_text = f"<strong>Telepon:</strong> {buyer_phone}<br>" if buyer_phone else ""
        message_text = f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 15px;">
            <strong>Pesan Tambahan:</strong>
            <p>{message}</p>
        </div>
        """ if message else ""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
                    <h2 style="margin: 0;">Product Inquiry</h2>
                </div>
                
                <div style="background-color: #ffffff; padding: 30px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px;">
                    <p>Kepada Yth. <strong>{supplier_name}</strong>,</p>
                    
                    <p>Kami tertarik dengan produk Anda dan ingin menanyakan lebih lanjut mengenai:</p>
                    
                    <div style="background-color: #e8f5e9; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0;">
                        <strong style="font-size: 18px; color: #2e7d32;">{product_name}</strong>
                    </div>
                    
                    <h3 style="color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 5px;">
                        Detail Inquiry
                    </h3>
                    
                    {quantity_text}
                    
                    <h3 style="color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 5px; margin-top: 25px;">
                        Kontak Pembeli
                    </h3>
                    
                    <strong>Nama:</strong> {buyer_name}<br>
                    <strong>Email:</strong> {buyer_email}<br>
                    {phone_text}
                    
                    {message_text}
                    
                    <p style="margin-top: 25px;">
                        Mohon informasi lebih lanjut mengenai:
                    </p>
                    <ul>
                        <li>Harga per unit</li>
                        <li>Minimum order quantity (MOQ)</li>
                        <li>Waktu pengiriman</li>
                        <li>Metode pembayaran</li>
                        <li>Ketersediaan stok</li>
                    </ul>
                    
                    <p>Kami menunggu balasan Anda segera. Terima kasih atas perhatiannya!</p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                        <p><strong>Salam hormat,</strong><br>
                        {buyer_name}<br>
                        {buyer_email}</p>
                        
                        <p style="margin-top: 15px; font-style: italic;">
                            Email ini dikirim secara otomatis melalui TrendScout AI - Platform Supplier Discovery
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_inquiry_email_text(
        self,
        supplier_name: str,
        product_name: str,
        buyer_name: str,
        buyer_email: str,
        buyer_phone: Optional[str],
        quantity: Optional[int],
        message: Optional[str]
    ) -> str:
        """Generate plain text email body for supplier inquiry"""
        
        quantity_text = f"Jumlah: {quantity} unit\n" if quantity else ""
        phone_text = f"Telepon: {buyer_phone}\n" if buyer_phone else ""
        message_text = f"\nPesan Tambahan:\n{message}\n" if message else ""
        
        text = f"""
PRODUCT INQUIRY
================

Kepada Yth. {supplier_name},

Kami tertarik dengan produk Anda dan ingin menanyakan lebih lanjut mengenai:

PRODUK: {product_name}

DETAIL INQUIRY
--------------
{quantity_text}

KONTAK PEMBELI
--------------
Nama: {buyer_name}
Email: {buyer_email}
{phone_text}
{message_text}

Mohon informasi lebih lanjut mengenai:
- Harga per unit
- Minimum order quantity (MOQ)
- Waktu pengiriman
- Metode pembayaran
- Ketersediaan stok

Kami menunggu balasan Anda segera. Terima kasih atas perhatiannya!

Salam hormat,
{buyer_name}
{buyer_email}

---
Email ini dikirim secara otomatis melalui TrendScout AI - Platform Supplier Discovery
        """
        
        return text.strip()


# Global instance
email_service = EmailService()
