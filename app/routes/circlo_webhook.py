"""
GetCirclo Webhook Handler - Agent Integration
Handles incoming conversations from GetCirclo platform
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
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
        
        # Generate natural language response based on result
        response_text = await _generate_natural_response(
            result=result,
            user_name=user_name,
            query=payload.message
        )
        
        logger.info(f"[GetCirclo Webhook] Generated response length: {len(response_text)} chars")
        
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
    """Format bestsellers results into natural response"""
    bestsellers = results.get('bestsellers', [])
    
    if not bestsellers:
        return (
            f"Hai {user_name}! Saya tidak menemukan produk bestseller saat ini. "
            f"Coba cari kategori lain? 🔍"
        )
    
    response = f"🔥 Hai {user_name}! Saya menemukan **{len(bestsellers)} produk terlaris** untuk Anda:\n\n"
    
    for i, product in enumerate(bestsellers[:5], 1):
        name = product.get('name', 'Unknown')
        rating = product.get('rating', 0)
        total_sold = product.get('total_sold', 0)
        price = product.get('price_range', 'N/A')
        platform = product.get('platform', 'Unknown')
        shop = product.get('shop_name', 'Unknown')
        
        response += f"**{i}. {name}**\n"
        response += f"   ⭐ Rating: {rating}/5.0\n"
        response += f"   🛒 Terjual: {total_sold:,} unit\n"
        response += f"   💰 Harga: {price}\n"
        response += f"   🏪 Platform: {platform} - {shop}\n\n"
    
    # Add supplier info if available
    suppliers = results.get('suppliers_by_product', {})
    if suppliers:
        response += f"\n✅ Saya juga menemukan **{len(suppliers)} supplier** untuk produk-produk ini!\n"
        response += "Mau saya carikan detail kontak supplier-nya? 📞\n"
    
    return response

def _format_suppliers_response(results: Dict[str, Any], user_name: str) -> str:
    """Format suppliers results into natural response"""
    suppliers = results.get('suppliers', [])
    
    if not suppliers:
        return (
            f"Hai {user_name}! Belum ada supplier yang ditemukan untuk produk ini. "
            f"Coba produk lain? 🔍"
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
