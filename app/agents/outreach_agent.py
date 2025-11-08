import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client as TwilioClient

from app.models.schemas import Supplier, OutreachMessage
from app.config import get_settings
from app.integrations.getcirclo_client import GetCircloClient

logger = logging.getLogger(__name__)
settings = get_settings()

class OutreachAgent:
    """Agent to contact suppliers via WhatsApp and Email"""
    
    def __init__(self):
        self.name = "Outreach Agent"
        self.getcirclo = GetCircloClient()
        self.twilio_client = TwilioClient(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.use_getcirclo = settings.getcirclo_whatsapp_enabled
        
    async def contact_suppliers(
        self,
        product_name: str,
        quantity: int,
        suppliers: List[Supplier],
        channels: List[str] = ["whatsapp", "email"]
    ) -> List[OutreachMessage]:
        """Main method to contact suppliers via multiple channels"""
        logger.info(f"Starting outreach to {len(suppliers)} suppliers")
        
        messages = []
        
        for supplier in suppliers:
            supplier_messages = await self._contact_supplier(
                supplier,
                product_name,
                quantity,
                channels
            )
            messages.extend(supplier_messages)
            
        return messages
        
    async def _contact_supplier(
        self,
        supplier: Supplier,
        product_name: str,
        quantity: int,
        channels: List[str]
    ) -> List[OutreachMessage]:
        """Contact a single supplier via specified channels"""
        messages = []
        
        message_content = self._generate_message(
            supplier,
            product_name,
            quantity
        )
        
        tasks = []
        
        if "whatsapp" in channels and supplier.phone:
            tasks.append(
                self._send_whatsapp(supplier, message_content)
            )
            
        if "email" in channels and supplier.email:
            tasks.append(
                self._send_email(supplier, product_name, message_content)
            )
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, OutreachMessage):
                messages.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Failed to send message: {str(result)}")
                
        return messages
        
    async def _send_whatsapp(
        self,
        supplier: Supplier,
        message: str
    ) -> OutreachMessage:
        """Send message via WhatsApp using GetCirclo or Twilio"""
        try:
            logger.info(f"Sending WhatsApp to {supplier.name}")
            
            phone_number = self._format_phone_number(supplier.phone)
            
            if self.use_getcirclo:
                result = await self.getcirclo.send_whatsapp_message(
                    phone_number=phone_number,
                    message=message
                )
                
                status = "sent" if result.get("success") else "failed"
                
            else:
                message_result = await asyncio.to_thread(
                    self.twilio_client.messages.create,
                    from_=f"whatsapp:{settings.twilio_whatsapp_number}",
                    body=message,
                    to=f"whatsapp:{phone_number}"
                )
                status = "sent"
            
            outreach_msg = OutreachMessage(
                supplier_id=f"{supplier.marketplace}_{supplier.store_name}",
                supplier_name=supplier.name,
                channel="whatsapp",
                message=message,
                status=status,
                sent_at=datetime.now()
            )
            
            logger.info(f"WhatsApp sent successfully to {supplier.name}")
            return outreach_msg
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp to {supplier.name}: {str(e)}")
            
            return OutreachMessage(
                supplier_id=f"{supplier.marketplace}_{supplier.store_name}",
                supplier_name=supplier.name,
                channel="whatsapp",
                message=message,
                status="failed",
                sent_at=datetime.now()
            )
            
    async def _send_email(
        self,
        supplier: Supplier,
        product_name: str,
        message: str
    ) -> OutreachMessage:
        """Send message via Email"""
        try:
            logger.info(f"Sending email to {supplier.name}")
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Inquiry: {product_name} - Potential Bulk Order"
            msg['From'] = settings.smtp_from_email
            msg['To'] = supplier.email
            
            text_part = MIMEText(message, 'plain')
            html_part = MIMEText(
                self._generate_html_email(supplier, message),
                'html'
            )
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            await aiosmtplib.send(
                msg,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_username,
                password=settings.smtp_password,
                start_tls=True
            )
            
            outreach_msg = OutreachMessage(
                supplier_id=f"{supplier.marketplace}_{supplier.store_name}",
                supplier_name=supplier.name,
                channel="email",
                message=message,
                status="sent",
                sent_at=datetime.now()
            )
            
            logger.info(f"Email sent successfully to {supplier.name}")
            return outreach_msg
            
        except Exception as e:
            logger.error(f"Error sending email to {supplier.name}: {str(e)}")
            
            return OutreachMessage(
                supplier_id=f"{supplier.marketplace}_{supplier.store_name}",
                supplier_name=supplier.name,
                channel="email",
                message=message,
                status="failed",
                sent_at=datetime.now()
            )
            
    def _generate_message(
        self,
        supplier: Supplier,
        product_name: str,
        quantity: int
    ) -> str:
        """Generate personalized message for supplier"""
        
        message = f"""Halo {supplier.name},

Saya tertarik dengan produk {product_name} yang dijual di toko Anda ({supplier.store_name}) di {supplier.marketplace}.

Detail kebutuhan saya:
- Produk: {product_name}
- Jumlah: {quantity} pcs
- Lokasi pengiriman: Indonesia

Mohon informasi mengenai:
1. Harga untuk pembelian {quantity} pcs (apakah ada harga grosir?)
2. Ketersediaan stok saat ini
3. Waktu pengiriman
4. Metode pembayaran yang tersedia
5. Garansi/return policy

Saya melihat rating toko Anda sangat baik ({supplier.rating}/5.0) dan saya tertarik untuk bekerja sama jangka panjang.

Mohon informasi lebih lanjut. Terima kasih!

Best regards,
TrendScout Team"""

        return message
        
    def _generate_html_email(self, supplier: Supplier, message: str) -> str:
        """Generate HTML version of email"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
        .footer {{ text-align: center; padding: 10px; color: #888; font-size: 12px; }}
        .highlight {{ background-color: #ffffcc; padding: 2px 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>TrendScout Supplier Connector</h2>
        </div>
        <div class="content">
            <p>{message.replace(chr(10), '<br>')}</p>
        </div>
        <div class="footer">
            <p>This is an automated message from TrendScout Platform</p>
            <p>Marketplace: {supplier.marketplace} | Rating: {supplier.rating}/5.0</p>
        </div>
    </div>
</body>
</html>
"""
        return html
        
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number to international format"""
        phone = phone.strip().replace(' ', '').replace('-', '')
        
        if phone.startswith('0'):
            phone = '+62' + phone[1:]
        elif not phone.startswith('+'):
            phone = '+62' + phone
            
        return phone
        
    async def generate_outreach_summary(
        self,
        messages: List[OutreachMessage]
    ) -> Dict[str, Any]:
        """Generate summary of outreach results"""
        
        total = len(messages)
        sent = len([m for m in messages if m.status == "sent"])
        failed = len([m for m in messages if m.status == "failed"])
        
        by_channel = {}
        for msg in messages:
            if msg.channel not in by_channel:
                by_channel[msg.channel] = {"sent": 0, "failed": 0}
            by_channel[msg.channel][msg.status] += 1
            
        summary = {
            "total_messages": total,
            "sent": sent,
            "failed": failed,
            "success_rate": (sent / total * 100) if total > 0 else 0,
            "by_channel": by_channel,
            "messages": messages
        }
        
        return summary
