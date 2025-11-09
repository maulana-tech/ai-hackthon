"""
GetCirclo Webhook Handler - Agent Integration
Handles incoming conversations from GetCirclo platform
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from urllib.parse import quote
from datetime import datetime
import logging

from app.agents.super_agent import SuperAgent
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/circlo-webhook", tags=["circlo-webhook"])

# Initialize SuperAgent
super_agent = SuperAgent()

class ConversationMessage(BaseModel):
    """Single message in conversation history"""
    role: str  # "user" or "assistant"
    content: str

class UserContext(BaseModel):
    """User preference context from GetCirclo"""
    id: str
    name: str
    preferredKeywords: Optional[List[str]] = []
    preferredNiches: Optional[List[str]] = []

class ProfileContext(BaseModel):
    """Agent profile context"""
    id: str
    name: str
    niche: str

class CircloWebhookPayload(BaseModel):
    """
    Payload received from GetCirclo when user sends message to agent
    
    Structure as per CIRCLO.md documentation:
    {
      "history": [...previous messages...],
      "message": "current user message",
      "user": {...user preferences...},
      "profile": {...agent identity...}
    }
    """
    history: List[ConversationMessage] = Field(default_factory=list)
    message: str = Field(..., description="Current user message")
    user: UserContext
    profile: ProfileContext

class CircloWebhookResponse(BaseModel):
    """
    Response format expected by GetCirclo
    
    Must return either:
    {"response": "agent reply"}
    or
    {"message": "agent reply"}
    """
    response: str = Field(..., description="Agent's reply to user")

@router.post("/hook", response_model=CircloWebhookResponse)
async def circlo_webhook_handler(payload: CircloWebhookPayload, request: Request):
    """
    Main webhook endpoint for GetCirclo agent integration
    
    This endpoint receives user conversations from GetCirclo platform and
    routes them through our SuperAgent for intelligent responses.
    
    Flow:
    1. Receive conversation from GetCirclo
    2. Extract user intent and context
    3. Route to appropriate agent (BestsellerFinder, SupplierScout, etc)
    4. Generate intelligent response
    5. Return response to GetCirclo
    
    GetCirclo will:
    - Forward user messages to this endpoint
    - Provide conversation history
    - Include user preferences for personalization
    - Expect response within 30 seconds
    """
    try:
        logger.info(
            f"[GetCirclo Webhook] Received message from user: {payload.user.name} "
            f"(ID: {payload.user.id})"
        )
        logger.info(f"[GetCirclo Webhook] Message: {payload.message}")
        logger.info(f"[GetCirclo Webhook] History length: {len(payload.history)}")
        
        # Extract user context for personalization
        user_id = payload.user.id
        user_name = payload.user.name
        user_keywords = payload.user.preferredKeywords or []
        user_niches = payload.user.preferredNiches or []
        
        logger.info(
            f"[GetCirclo Webhook] User context - "
            f"Keywords: {user_keywords}, Niches: {user_niches}"
        )
        
        # Build conversation context for better responses
        conversation_context = []
        for msg in payload.history[-5:]:  # Last 5 messages for context
            conversation_context.append(f"{msg.role}: {msg.content}")
        
        context_str = "\n".join(conversation_context) if conversation_context else ""
        
        # Enhance query with user context
        enhanced_query = payload.message
        if user_keywords:
            # Add implicit context without being too verbose
            logger.info(f"[GetCirclo Webhook] User interested in: {', '.join(user_keywords)}")
        
        # Execute query through SuperAgent
        # SuperAgent will:
        # 1. Classify intent (find_trending, find_suppliers, find_bestsellers, etc)
        # 2. Route to appropriate sub-agent
        # 3. Generate intelligent response
        logger.info(f"[GetCirclo Webhook] Processing query through SuperAgent...")
        
        result = await super_agent.execute(
            query=enhanced_query,
            user_id=user_id,
            context=context_str
        )
        
        logger.info(f"[GetCirclo Webhook] SuperAgent result status: {result.get('status')}")
        logger.info(f"[GetCirclo Webhook] Detected intent: {result.get('intent')}")
        
        # Auto-generate marketing campaign for bestseller results
        intent = result.get('intent')
        if intent == 'find_bestsellers' and result.get('status') == 'success':
            results_data = result.get('results', {})
            bestsellers = results_data.get('bestsellers', [])
            
            if bestsellers:
                logger.info(f"[GetCirclo Webhook] Auto-generating marketing campaigns for {len(bestsellers)} products...")
                
                # Generate campaigns for top products (limit to 3)
                campaign_result = await super_agent.execute(
                    query=f"Buatkan kampanye marketing untuk produk: {', '.join([p.get('name', '') for p in bestsellers[:3]])}",
                    user_id=user_id,
                    context=context_str
                )
                
                # Merge campaign data into result
                if campaign_result.get('status') == 'success':
                    result['campaign_data'] = campaign_result.get('results', {})
                    logger.info(f"[GetCirclo Webhook] Campaigns auto-generated successfully")
        
        # Generate natural language response based on result
        response_text = await _generate_natural_response(
            result=result,
            user_name=user_name,
            query=payload.message
        )
        
        logger.info(f"[GetCirclo Webhook] Generated response length: {len(response_text)} chars")
        
        # Note: Memory is saved inside super_agent.execute()
        # No need to save again here
        
        return CircloWebhookResponse(response=response_text)
        
    except Exception as e:
        logger.error(f"[GetCirclo Webhook] Error processing message: {str(e)}")
        logger.exception(e)
        
        # Return friendly error message to user
        error_response = (
            f"Maaf {payload.user.name}, saya sedang mengalami kendala teknis. "
            f"Silakan coba lagi dalam beberapa saat. 🙏"
        )
        
        return CircloWebhookResponse(response=error_response)

async def _generate_natural_response(
    result: Dict[str, Any],
    user_name: str,
    query: str
) -> str:
    """
    Generate natural, conversational response from agent result
    
    Converts technical agent output into friendly, actionable responses
    """
    status = result.get('status')
    intent = result.get('intent')
    results_data = result.get('results', {})
    
    if status == 'failed':
        return (
            f"Maaf {user_name}, saya tidak dapat memproses permintaan Anda saat ini. "
            f"Bisakah Anda coba dengan kata-kata yang berbeda? 😊"
        )
    
    # Handle different intents
    if intent == 'find_bestsellers':
        return _format_bestsellers_response(results_data, user_name)
    
    elif intent == 'find_suppliers':
        return _format_suppliers_response(results_data, user_name)
    
    elif intent == 'find_trending_products':
        return _format_trending_response(results_data, user_name)
    
    elif intent == 'find_trending_suppliers':
        return _format_trending_suppliers_response(results_data, user_name)
    
    elif intent == 'contact_suppliers':
        return _format_email_response(results_data, user_name)
    
    elif intent == 'create_campaign':
        return _format_campaign_response(results_data, user_name)
    
    else:
        # Generic response
        summary = results_data.get('summary', '')
        if summary:
            return f"Hai {user_name}! 👋\n\n{summary}"
        else:
            return (
                f"Hai {user_name}! Saya sudah memproses permintaan Anda. "
                f"Silakan cek detail hasilnya! 😊"
            )

def _format_bestsellers_response(results: Dict[str, Any], user_name: str) -> str:
    """Format bestsellers results into natural response with CTA buttons"""
    bestsellers = results.get('bestsellers', [])
    
    if not bestsellers:
        return (
            f"Hai {user_name}! 🔍\n\n"
            f"Saya belum menemukan produk bestseller yang sesuai kriteria.\n\n"
            f"**Tips:**\n"
            f"• Coba kata kunci yang lebih umum (misal: 'fashion' bukan 'baju batik premium')\n"
            f"• Gunakan kategori populer: skincare, elektronik, fashion, home decor\n"
            f"• Coba marketplace spesifik: 'produk terlaris di Tokopedia'\n\n"
            f"Atau tanyakan: \"Apa produk yang sedang trending?\""
        )
    
    response = f"🔥 Hai {user_name}! Saya menemukan **{len(bestsellers)} produk terlaris** untuk Anda:\n\n"
    
    for i, product in enumerate(bestsellers[:5], 1):
        name = product.get('name', 'Unknown')
        rating = product.get('rating', 0)
        total_sold = product.get('total_sold', 0)
        price = product.get('price_range', 'N/A')
        platform = product.get('platform', 'Unknown')
        shop = product.get('shop_name', 'Unknown')
        product_url = product.get('product_url', '') or product.get('url', '')
        
        # Format with proper line breaks for better readability
        response += f"**{i}. {name}**\n\n"
        response += f"⭐ Rating: {rating}/5.0\n\n"
        response += f"🛒 Terjual: {total_sold:,} unit\n\n"
        response += f"💰 Harga: {price}\n\n"
        response += f"🏪 {platform}\n"
        response += f"Toko: {shop}\n"
        
        # Add description with supplier email if available (especially for Shopee fallback data)
        description = product.get('description', '')
        if description and '@' in description:
            # Extract and highlight email
            response += f"\n📧 **Contact:** {description}\n"
        elif description:
            # Show description for context
            desc_short = description[:150] + ('...' if len(description) > 150 else '')
            response += f"\n💬 {desc_short}\n"
        
        # Add CTA button if product URL available
        if product_url:
            response += f"\n🔗 Lihat Produk:\n{product_url}\n"
        
        response += "\n" + "─" * 30 + "\n\n"
    
    # Add supplier info if available
    suppliers = results.get('suppliers_by_product', {})
    if suppliers:
        response += f"\n✅ Saya juga menemukan **{len(suppliers)} supplier** untuk produk-produk ini!\n"
        response += "Mau saya carikan detail kontak supplier-nya? 📞\n"
    
    # Check if campaign data is available
    campaign_data = results.get('campaign_data', {})
    campaigns = campaign_data.get('campaigns', [])
    
    if campaigns:
        # Add auto-generated campaign section
        response += "\n" + "═" * 40 + "\n"
        response += "\n🎨 **AI MARKETING CAMPAIGN AUTO-GENERATED!**\n\n"
        
        for i, campaign in enumerate(campaigns[:3], 1):
            product = campaign.get('product', 'Product')
            response += f"**Campaign {i}: {product}**\n\n"
            
            # Tagline
            tagline = campaign.get('tagline', '')
            if tagline:
                response += f"💡 {tagline}\n\n"
            
            # Budget
            budget_data = campaign.get('budget', {})
            if isinstance(budget_data, str):
                response += f"💰 Budget: {budget_data}\n"
            else:
                total_budget = budget_data.get('total_budget', 'N/A')
                response += f"💰 Budget Total: {total_budget}\n"
                
                allocations = budget_data.get('allocations', [])
                if allocations:
                    response += f"📊 Breakdown:\n"
                    for alloc in allocations[:3]:
                        channel = alloc.get('channel', '')
                        percentage = alloc.get('percentage', 0)
                        amount = alloc.get('amount', '')
                        response += f"   • {channel}: {percentage}% ({amount})\n"
            
            # Duration
            duration = campaign.get('duration', 30)
            response += f"\n📅 Durasi: {duration} hari\n"
            
            # Schedule preview
            schedule_data = campaign.get('schedule', {})
            if schedule_data:
                phases = schedule_data.get('phases', [])
                if phases:
                    response += f"\n🎯 Campaign Phases:\n"
                    for phase in phases[:3]:
                        phase_name = phase.get('phase', '')
                        week = phase.get('week', '')
                        response += f"   • {phase_name} ({week})\n"
            
            response += "\n"
        
        # Download links
        response += "─" * 40 + "\n"
        response += "\n**📥 Download Campaign:**\n\n"
        
        # Google Sheets export
        sheets_create = "https://docs.google.com/spreadsheets/create"
        response += f"📊 Export ke Google Sheets\n"
        response += f"   {sheets_create}\n"
        response += f"   Copy campaign data ke sheet untuk tracking\n\n"
        
        # Google Docs export
        gdocs_create = "https://docs.google.com/document/create"
        response += f"📄 Export ke Google Docs\n"
        response += f"   {gdocs_create}\n"
        response += f"   Copy campaign details untuk presentation\n\n"
        
        response += "💡 Campaign siap dijalankan! Data lengkap tersedia untuk export.\n"
    else:
        # Original CTA if no campaign generated
        response += "**🎯 Langkah Selanjutnya:**\n\n"
        
        # Create Gmail compose link with URL encoding
        gmail_subject = "Inquiry Produk - " + (bestsellers[0].get('name', 'Product')[:50] if bestsellers else "Product Inquiry")
        gmail_body = "Halo,\n\nSaya tertarik dengan produk Anda. Mohon informasi lebih lanjut mengenai harga dan ketersediaan stok.\n\nTerima kasih."
        gmail_link = f"https://mail.google.com/mail/?view=cm&fs=1&su={quote(gmail_subject)}&body={quote(gmail_body)}"
        
        response += f"📧 **Email Supplier:**\n\n"
        response += f"{gmail_link}\n\n"
        response += "─" * 30 + "\n\n"
        
        # Google Docs template for campaign planning
        gdocs_template = "https://docs.google.com/document/create"
        response += f"🎨 **Campaign Doc:**\n\n"
        response += f"{gdocs_template}\n\n"
        response += "─" * 30 + "\n\n"
        
        response += "💡 **Buat Kampanye Marketing:**\n\n"
        response += "Ketik: \"Buat kampanye marketing\"\n"
    
    return response

def _format_suppliers_response(results: Dict[str, Any], user_name: str) -> str:
    """Format suppliers results into natural response"""
    suppliers = results.get('suppliers', [])
    
    if not suppliers:
        return (
            f"Hai {user_name}! 📦\n\n"
            f"Belum menemukan supplier untuk produk ini.\n\n"
            f"**Saran:**\n"
            f"• Pastikan nama produk spesifik (misal: 'sepatu sneakers' bukan 'alas kaki')\n"
            f"• Cari produk yang umum tersedia di marketplace\n"
            f"• Gunakan kata kunci bahasa Indonesia\n\n"
            f"Atau coba: \"Carikan supplier untuk [nama produk]\""
        )
    
    response = f"📦 Hai {user_name}! Saya menemukan **{len(suppliers)} supplier** untuk Anda:\n\n"
    
    for i, supplier in enumerate(suppliers[:5], 1):
        name = supplier.get('name', 'Unknown')
        location = supplier.get('location', 'Unknown')
        whatsapp = supplier.get('whatsapp', 'N/A')
        rating = supplier.get('rating', 0)
        verified = supplier.get('verified', False)
        
        response += f"**{i}. {name}**\n"
        response += f"   📍 Lokasi: {location}\n"
        response += f"   ⭐ Rating: {rating}/5.0\n"
        if whatsapp != 'N/A':
            response += f"   📱 WhatsApp: {whatsapp}\n"
        if verified:
            response += f"   ✅ Verified Supplier\n"
        response += "\n"
    
    response += "\nMau saya hubungkan dengan supplier ini via WhatsApp? 📞"
    
    return response

def _format_trending_response(results: Dict[str, Any], user_name: str) -> str:
    """Format trending products response"""
    products = results.get('trending_products', [])
    
    if not products:
        return f"Hai {user_name}! Belum ada trending products yang ditemukan. 🔍"
    
    response = f"📈 Hai {user_name}! Ini **{len(products)} produk trending** saat ini:\n\n"
    
    for i, product in enumerate(products[:5], 1):
        name = product.get('name', 'Unknown')
        trend_score = product.get('trend_score', 0)
        growth = product.get('growth_percentage', 0)
        
        response += f"**{i}. {name}**\n"
        response += f"   📊 Trend Score: {trend_score}/100\n"
        response += f"   📈 Growth: +{growth}%\n\n"
    
    response += "\nMau saya carikan supplier untuk produk ini? 🔍"
    
    return response

def _format_trending_suppliers_response(results: Dict[str, Any], user_name: str) -> str:
    """Format trending suppliers response"""
    products = results.get('trending_products', [])
    suppliers = results.get('suppliers', [])
    
    response = f"🔥 Hai {user_name}! Saya menemukan trending products + suppliers:\n\n"
    
    if products:
        top_product = products[0]
        response += f"**Top Product**: {top_product.get('name')}\n"
        response += f"📊 Trend Score: {top_product.get('trend_score')}/100\n\n"
    
    if suppliers:
        response += f"✅ **{len(suppliers)} Supplier** tersedia!\n"
        for i, sup in enumerate(suppliers[:3], 1):
            response += f"{i}. {sup.get('name')} ({sup.get('location')})\n"
    
    return response

def _format_email_response(results: Dict[str, Any], user_name: str) -> str:
    """Format email sending response"""
    email_status = results.get('email_status', 'unknown')
    sent = results.get('sent', 0)
    failed = results.get('failed', 0)
    total = results.get('total', 0)
    message = results.get('message', '')
    suppliers_contacted = results.get('suppliers_contacted', [])
    details = results.get('details', [])
    
    # Success response
    if email_status == 'success':
        response = f"✅ Hai {user_name}! {message}\n\n"
        response += f"📧 **Email Status:**\n"
        response += f"   ✅ Berhasil dikirim: {sent}\n"
        response += f"   📊 Total supplier: {total}\n\n"
        
        if suppliers_contacted:
            response += f"**Supplier yang dihubungi:**\n"
            for i, supplier in enumerate(suppliers_contacted[:5], 1):
                response += f"{i}. {supplier}\n"
            response += "\n"
        
        response += "💡 Supplier akan menerima detail inquiry Anda.\n"
        response += "Mereka akan menghubungi Anda kembali via email/WhatsApp!\n"
        
        # Add next action CTA with plain URLs (GetCirclo auto-detects links)
        response += "\n" + "─" * 40 + "\n"
        response += "\n**🎯 Selanjutnya:**\n\n"
        
        # Google Sheets for campaign tracking
        sheets_template = "https://docs.google.com/spreadsheets/create"
        response += f"📊 Buat Campaign Tracking Sheet\n"
        response += f"   {sheets_template}\n\n"
        
        # Google Docs for campaign planning
        gdocs_campaign = "https://docs.google.com/document/create"
        response += f"🎨 Buat Campaign Planning Doc\n"
        response += f"   {gdocs_campaign}\n\n"
        
        response += "💡 Atau ketik: \"Buat kampanye marketing\" untuk AI-generated campaign\n"
        
    # Partial success
    elif email_status == 'partial':
        response = f"⚠️ Hai {user_name}! Email terkirim sebagian.\n\n"
        response += f"📧 **Status:**\n"
        response += f"   ✅ Berhasil: {sent}\n"
        response += f"   ❌ Gagal: {failed}\n"
        response += f"   📊 Total: {total}\n\n"
        
        # Show successful contacts
        success_suppliers = [s for s in details if s.get('status') == 'success']
        if success_suppliers:
            response += f"**Supplier yang berhasil dihubungi:**\n"
            for i, detail in enumerate(success_suppliers[:3], 1):
                response += f"{i}. {detail.get('supplier')}\n"
        
    # Failed
    else:
        response = f"❌ Hai {user_name}! Maaf, {message}\n\n"
        response += f"Mohon coba lagi atau hubungi kami untuk bantuan. 🙏\n"
    
    return response

def _generate_campaign_document(campaign: Dict[str, Any]) -> str:
    """
    Generate complete campaign document content that can be copied to Google Docs
    """
    product = campaign.get('product', 'Product')
    budget = campaign.get('budget', {})
    schedule = campaign.get('schedule', {})
    platforms = campaign.get('platforms', {})
    kpis = campaign.get('kpis', [])
    
    doc_content = f"""
MARKETING CAMPAIGN PLAN
========================

Product: {product}
Created: {datetime.now().strftime('%Y-%m-%d')}

1. CAMPAIGN OVERVIEW
-------------------
Budget: {budget.get('total_budget', 'Rp 5.000.000')}
Duration: {schedule.get('duration_days', 30)} days
Target Audience: General consumers

2. BUDGET ALLOCATION
------------------
"""
    
    allocation = budget.get('allocation', {})
    if allocation:
        for channel, data in allocation.items():
            if isinstance(data, dict):
                doc_content += f"{channel.replace('_', ' ').title()}: {data.get('percentage', '')} - {data.get('amount', '')}\n"
    
    doc_content += f"""
3. CAMPAIGN SCHEDULE
-------------------
"""
    
    phases = schedule.get('phases', [])
    if phases:
        for phase in phases:
            doc_content += f"Week {phase.get('week', '')}: {phase.get('phase', '')} - {phase.get('activities', '')}\n"
    
    doc_content += f"""
4. PLATFORM STRATEGY
-------------------
"""
    
    if platforms:
        for platform, strategy in platforms.items():
            doc_content += f"{platform}: {strategy}\n"
    
    doc_content += f"""
5. KEY PERFORMANCE INDICATORS
---------------------------
"""
    
    if kpis:
        for kpi in kpis:
            doc_content += f"• {kpi}\n"
    
    return doc_content.strip()

def _format_campaign_response(results: Dict[str, Any], user_name: str) -> str:
    """Format marketing campaign response"""
    campaigns_created = results.get('campaigns_created', 0)
    campaigns = results.get('campaigns', [])
    campaign = results.get('campaign')
    message = results.get('message', '')
    
    # Multiple campaigns
    if campaigns:
        response = f"🎯 Hai {user_name}! {message}\n\n"
        response += f"📊 **{campaigns_created} Kampanye Marketing Siap!**\n\n"
        
        for i, camp in enumerate(campaigns, 1):
            response += f"**{i}. {camp.get('product')}**\n"
            
            # Tagline
            tagline = camp.get('tagline', '')
            if tagline:
                response += f"   💡 {tagline}\n"
            
            # Budget
            budget = camp.get('budget', 'N/A')
            response += f"   💰 Budget: {budget}\n"
            
            # Duration
            duration = camp.get('duration', 30)
            response += f"   📅 Durasi: {duration} hari\n"
            
            # Sheet URL
            sheet_url = camp.get('sheet_url')
            if sheet_url:
                response += f"   📊 [Tracking Sheet]({sheet_url})\n"
            
            response += "\n"
        
        response += "✨ **Fitur Kampanye:**\n"
        response += "- Campaign content & messaging\n"
        response += "- Schedule & timeline\n"
        response += "- Budget allocation\n"
        response += "- Platform strategies\n"
        response += "- KPIs & recommendations\n\n"
        
        response += "📈 Semua data tersimpan di Google Sheets untuk tracking!\n"
        
        # Add action buttons with plain URLs (better formatting)
        response += "\n" + "─" * 40 + "\n\n"
        response += "**🎯 Quick Actions:**\n\n"
        
        # Google Sheets for tracking
        sheets_create = "https://docs.google.com/spreadsheets/create"
        response += f"📊 **Campaign Tracking Sheet**\n"
        response += f"{sheets_create}\n\n"
        
        # Gmail compose for sharing (URL encoded)
        campaign_names = ", ".join([c.get('product', '') for c in campaigns[:2]])
        gmail_subject = f"Marketing Campaign - {campaign_names}"
        gmail_body = f"Hi Team,\n\nBerikut {len(campaigns)} campaign marketing yang sudah dibuat.\n\nSilakan review dan execute."
        gmail_campaign = f"https://mail.google.com/mail/?view=cm&fs=1&su={quote(gmail_subject)}&body={quote(gmail_body)}"
        response += f"📧 **Email ke Tim**\n"
        response += f"{gmail_campaign}\n\n"
        
        # Google Calendar for scheduling
        gcal_link = "https://calendar.google.com/calendar/u/0/r/eventedit"
        response += f"📅 **Schedule Campaign**\n"
        response += f"{gcal_link}\n"
        
    # Single campaign
    elif campaign:
        product = campaign.get('product', 'Product')
        response = f"🎯 Hai {user_name}! Kampanye untuk **{product}** sudah siap!\n\n"
        
        # Generate complete campaign document content
        campaign_doc_content = _generate_campaign_document(campaign)
        
        # Content preview
        content = campaign.get('content', '')
        if content:
            try:
                import json
                content_json = json.loads(content)
                tagline = content_json.get('tagline', '')
                if tagline:
                    response += f"💡 **Tagline**: {tagline}\n\n"
            except:
                pass
        
        # Budget
        budget_data = campaign.get('budget', {})
        total_budget = budget_data.get('total_budget', 'N/A')
        response += f"💰 **Budget**: {total_budget}\n"
        
        # Allocation
        allocation = budget_data.get('allocation', {})
        if allocation:
            response += f"\n📊 **Budget Allocation**:\n"
            for channel, data in list(allocation.items())[:3]:
                if isinstance(data, dict):
                    percentage = data.get('percentage', '')
                    amount = data.get('amount', '')
                    response += f"   • {channel.replace('_', ' ').title()}: {percentage} ({amount})\n"
        
        # Schedule
        schedule = campaign.get('schedule', {})
        duration = schedule.get('duration_days', 30)
        response += f"\n📅 **Durasi**: {duration} hari\n"
        
        phases = schedule.get('phases', [])
        if phases:
            response += f"\n🎯 **Campaign Phases**:\n"
            for phase in phases[:3]:
                phase_name = phase.get('phase', '')
                week = phase.get('week', '')
                response += f"   • {phase_name} (Week {week})\n"
        
        # KPIs
        kpis = campaign.get('kpis', [])
        if kpis:
            response += f"\n📈 **Target KPIs**:\n"
            for kpi in kpis[:3]:
                response += f"   • {kpi}\n"
        
        # Document URLs (GitHub Gist)
        doc_url = campaign.get('sheet_url')  # View URL  
        raw_url = campaign.get('doc_url')  # Raw/Download URL
        
        # Automation Results (Next Steps Auto-Executed)
        automation = campaign.get('automation_results', {})
        if automation and automation.get('status') == 'completed':
            response += f"\n🤖 **Next Steps Auto-Executed!**\n\n"
            response += automation.get('summary', '')
            response += "\n"
        
        # Document Links
        if doc_url:
            response += f"\n📄 **Campaign Document:**\n\n"
            response += f"{doc_url}\n\n"
            if raw_url:
                response += f"📥 Download: {raw_url}\n\n"
            response += "💡 Klik untuk view complete campaign plan\n\n"
        
        # Automation Details
        if automation and automation.get('results'):
            auto_results = automation['results']
            
            # Content Calendar
            calendar = auto_results.get('3_content_calendar', {})
            if calendar.get('calendar'):
                total_posts = calendar.get('total_posts', 0)
                response += f"📅 **Content Calendar:** {total_posts} posts generated\n\n"
            
            # Budget Optimization
            budget_opt = auto_results.get('2_budget_optimization', {})
            if budget_opt.get('priority_channels'):
                channels = ', '.join(budget_opt['priority_channels'][:2])
                response += f"💰 **Budget:** Optimized untuk {channels}\n\n"
            
            # Tracking Setup - Show detailed tracking table
            tracking = auto_results.get('4_tracking_setup', {})
            if tracking.get('tracking_table'):
                tracking_table = tracking['tracking_table']
                campaign_info = tracking_table.get('campaign_info', {})
                budget_alloc = tracking_table.get('budget_allocation', {})
                
                response += f"📊 **Tracking Sheet Generated!**\n\n"
                
                if budget_alloc:
                    response += f"💰 **Budget Allocation:**\n"
                    response += f"Total Budget: Rp {campaign_info.get('total_budget', 5000000):,.0f}\n"
                    response += f"Duration: {campaign_info.get('duration', 30)} days\n"
                    response += f"Daily Budget: Rp {campaign_info.get('daily_budget', 166667):,.0f}\n\n"
                    
                    response += f"**Platform Breakdown:**\n"
                    for platform, data in budget_alloc.items():
                        daily = data.get('daily', 0)
                        response += f"• {platform}: {data['percentage']}%\n"
                        response += f"  Budget: Rp {data['amount']:,.0f}\n"
                        response += f"  Daily: Rp {daily:,.0f}\n\n"
                
                # Add tracking sheet structure info
                sheets = tracking_table.get('sheets_structure', {})
                if sheets:
                    response += f"📋 **5 Sheets Ready:**\n"
                    response += f"1. 📊 Overview Dashboard\n"
                    response += f"2. 📅 Daily Tracking (14 columns)\n"
                    response += f"3. 🚀 Platform Performance\n"
                    response += f"4. 💰 Budget Tracking (Main)\n"
                    response += f"5. 📈 KPI Dashboard\n\n"
                    
                    response += f"📥 **Copy to Google Sheets:**\n"
                    response += f"Structure tersimpan di campaign document\n\n"
            
            # Launch Checklist  
            checklist = auto_results.get('5_launch_checklist', {})
            if checklist.get('checklist'):
                total_tasks = checklist.get('total_tasks', 0)
                response += f"✅ **Launch Checklist:** {total_tasks} tasks ready\n\n"
        
        # Add quick actions
        response += "**🎯 Quick Actions:**\n\n"
        
        # Get product name for CTAs
        cta_product_name = campaign.get('product', 'Product')
        
        # Share via email
        if doc_url:
            gmail_subject = f"Campaign Plan: {cta_product_name}"
            gmail_body = f"Hi Team,\n\nCampaign plan untuk {cta_product_name} sudah siap!\n\nLihat detail lengkap:\n{doc_url}\n\nBudget: {budget_data.get('total_budget', 'N/A')}\nDurasi: {duration} hari"
            gmail_share = f"https://mail.google.com/mail/?view=cm&fs=1&su={quote(gmail_subject)}&body={quote(gmail_body)}"
            response += f"📧 **Share via Email:**\n\n"
            response += f"{gmail_share}\n\n"
            response += "─" * 30 + "\n\n"
        
        # Google Sheets for tracking
        sheets_url = f"https://docs.google.com/spreadsheets/create"
        response += f"📊 **Buat Tracking Sheet:**\n\n"
        response += f"{sheets_url}\n"
        response += f"(Import data dari campaign document)\n"
    
    else:
        response = f"Hai {user_name}! {message}\n"
    
    return response

@router.get("/webhook-info")
async def webhook_info():
    """
    Get information about webhook endpoint
    
    Use this to verify webhook is accessible
    """
    return {
        "status": "active",
        "endpoint": "/circlo-webhook/hook",
        "method": "POST",
        "description": "GetCirclo agent webhook handler",
        "documentation": "See docs/CIRCLO.md for integration details",
        "timeout": "30 seconds",
        "expected_payload": {
            "history": "List of conversation messages",
            "message": "Current user message",
            "user": "User context and preferences",
            "profile": "Agent profile information"
        },
        "response_format": {
            "response": "Agent's reply to user"
        }
    }
