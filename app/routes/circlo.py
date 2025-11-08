from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from app.agents.circlo_conversation_handler import CircloConversationHandler
from app.integrations.getcirclo_client import GetCircloClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/circlo", tags=["Circlo Integration"])

# Initialize clients
conversation_handler = CircloConversationHandler()
getcirclo_client = GetCircloClient()


# Pydantic Models
class ConversationMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class UserInfo(BaseModel):
    id: str
    name: str
    preferredKeywords: Optional[List[str]] = []
    preferredNiches: Optional[List[str]] = []


class ProfileInfo(BaseModel):
    id: str
    name: str
    niche: str


class CircloWebhookPayload(BaseModel):
    history: List[ConversationMessage] = Field(..., description="Conversation history")
    message: str = Field(..., description="Latest user message")
    user: UserInfo = Field(..., description="User information with preferences")
    profile: ProfileInfo = Field(..., description="Agent profile information")


class CreatePostRequest(BaseModel):
    profile: str = Field(..., description="Either 'general' or specific profile_id")
    media_type: str = Field(..., description="'image' or 'video'")
    media_source: str = Field(..., description="URL of media from Replicate")
    caption: str = Field(..., description="Post caption text")
    niche: Optional[str] = Field(None, description="Niche (required when profile is 'general')")
    keywords: Optional[List[str]] = Field(None, description="Optional keywords/hashtags")


class CreateAgentRequest(BaseModel):
    name: str = Field(..., description="Display name for the agent")
    username: str = Field(..., description="Unique handle")
    niche: str = Field(..., description="Primary niche the agent represents")
    avatar_url: str = Field(..., description="Public image URL for agent's avatar")
    endpoint: Optional[str] = Field(None, description="Optional HTTPS URL for custom agent endpoint")


@router.post("/circlo-hook")
async def circlo_webhook(payload: CircloWebhookPayload):
    """
    Custom endpoint for Circlo agent conversations
    
    This endpoint receives conversation requests from Circlo
    and returns AI-generated responses.
    
    Expected from Circlo:
    {
        "history": [{"role": "user", "content": "..."}],
        "message": "Latest user message",
        "user": {"id": "...", "name": "...", "preferredKeywords": []},
        "profile": {"id": "...", "name": "...", "niche": "..."}
    }
    
    Returns:
    {
        "response": "AI reply message"
    }
    """
    try:
        logger.info(f"Received Circlo webhook from user {payload.user.id}")
        
        # Convert Pydantic models to dicts
        history = [msg.model_dump() for msg in payload.history]
        user = payload.user.model_dump()
        profile = payload.profile.model_dump()
        
        # Process conversation
        response = await conversation_handler.handle_conversation(
            history=history,
            message=payload.message,
            user=user,
            profile=profile
        )
        
        logger.info(f"Circlo webhook processed successfully")
        
        return response
        
    except Exception as e:
        logger.error(f"Circlo webhook error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process conversation: {str(e)}"
        )


@router.post("/create-post")
async def create_post(request: CreatePostRequest):
    """
    Create a post on Circlo platform
    
    Args:
        profile: Either "general" or specific profile_id
        media_type: "image" or "video"
        media_source: URL of media from Replicate
        caption: Post caption text (required)
        niche: Niche (required when profile is "general")
        keywords: Optional keywords/hashtags
    
    Returns:
        Created post information
    """
    try:
        logger.info(f"Creating Circlo post (profile: {request.profile})")
        
        # Validate required fields
        if request.profile == "general" and not request.niche:
            raise HTTPException(
                status_code=400,
                detail="Niche is required when profile is 'general'"
            )
        
        # Create post via Circlo API
        result = await getcirclo_client.create_post(
            profile=request.profile,
            media_type=request.media_type,
            media_source=request.media_source,
            caption=request.caption,
            niche=request.niche,
            keywords=request.keywords
        )
        
        if result.get("success"):
            return {
                "success": True,
                "post": result.get("post"),
                "message": "Post created successfully on Circlo"
            }
        else:
            raise HTTPException(
                status_code=result.get("status_code", 500),
                detail=result.get("error", "Failed to create post")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create post error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create post: {str(e)}"
        )


@router.post("/create-agent")
async def create_agent(request: CreateAgentRequest):
    """
    Register an agent profile on Circlo
    
    Args:
        name: Display name for the agent
        username: Unique handle
        niche: Primary niche the agent represents
        avatar_url: Public image URL for agent's avatar
        endpoint: Optional HTTPS URL for custom agent endpoint
    
    Returns:
        Created agent profile information
    """
    try:
        logger.info(f"Creating Circlo agent: {request.username}")
        
        # Create agent via Circlo API
        result = await getcirclo_client.create_agent(
            name=request.name,
            username=request.username,
            niche=request.niche,
            avatar_url=request.avatar_url,
            endpoint=request.endpoint
        )
        
        if result.get("success"):
            return {
                "success": True,
                "agent": result.get("agent"),
                "message": f"Agent '{request.name}' created successfully on Circlo"
            }
        elif result.get("status_code") == 409:
            raise HTTPException(
                status_code=409,
                detail="Username already exists"
            )
        else:
            raise HTTPException(
                status_code=result.get("status_code", 500),
                detail=result.get("error", "Failed to create agent")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create agent error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.get("/user-preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """
    Get user preferences from Circlo
    
    Returns user's saved preferences including:
    - Preferred keywords
    - Preferred niches
    - Engagement history
    """
    try:
        logger.info(f"Getting user preferences for {user_id}")
        
        result = await getcirclo_client.get_user_preference(user_id)
        
        if result.get("success"):
            return {
                "success": True,
                "preference": result.get("preference")
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="User preferences not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user preferences error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user preferences: {str(e)}"
        )


@router.get("/user-preferences")
async def get_all_user_preferences(page: int = 1, limit: int = 10):
    """
    Get all user preferences with pagination
    
    Query Parameters:
    - page: Page number (default: 1)
    - limit: Items per page (default: 10)
    """
    try:
        logger.info(f"Getting all user preferences (page {page}, limit {limit})")
        
        result = await getcirclo_client.get_all_user_preferences(
            page=page,
            limit=limit
        )
        
        if result.get("success"):
            return {
                "success": True,
                "preferences": result.get("preferences", []),
                "pagination": result.get("pagination", {})
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to get user preferences"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get all user preferences error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user preferences: {str(e)}"
        )


@router.post("/send-whatsapp")
async def send_whatsapp_message(
    phone_number: str = Body(..., description="Recipient phone number"),
    message: str = Body(..., description="Message text")
):
    """
    Send WhatsApp message via Circlo
    
    Args:
        phone_number: Recipient phone number (international format)
        message: Message text to send
    """
    try:
        logger.info(f"Sending WhatsApp via Circlo to {phone_number}")
        
        result = await getcirclo_client.send_whatsapp_message(
            phone_number=phone_number,
            message=message
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": "WhatsApp message sent successfully",
                "message_id": result.get("message_id")
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to send WhatsApp message")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send WhatsApp error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send WhatsApp: {str(e)}"
        )


@router.get("/health")
async def circlo_health_check():
    """Check Circlo API connection health"""
    try:
        result = await getcirclo_client.health_check()
        
        return {
            "circlo_api": result.get("status", "unknown"),
            "whatsapp_enabled": result.get("whatsapp_enabled", False),
            "memory_enabled": result.get("memory_enabled", False),
            "success": result.get("success", False)
        }
        
    except Exception as e:
        logger.error(f"Circlo health check error: {str(e)}")
        return {
            "circlo_api": "error",
            "error": str(e),
            "success": False
        }
