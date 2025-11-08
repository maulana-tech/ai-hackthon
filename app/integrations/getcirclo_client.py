import asyncio
import logging
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class GetCircloClient:
    """
    GetCirclo Platform API Client
    
    Provides integration with GetCirclo's:
    - User Preferences API
    - Post Creation API
    - Agent Profile API
    - Custom Agent Endpoints
    - WhatsApp Messaging API
    
    Based on official GetCirclo API documentation
    """
    
    def __init__(self):
        self.api_key = settings.getcirclo_api_key
        self.jwt_token = settings.getcirclo_jwt_token
        self.base_url = "https://api.getcirclo.com/api"
        self.whatsapp_enabled = settings.getcirclo_whatsapp_enabled
        self.memory_enabled = settings.getcirclo_memory_enabled
        
        # Use JWT token if available, otherwise fallback to API key
        auth_token = self.jwt_token if self.jwt_token else self.api_key
        
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
    async def get_all_user_preferences(
        self,
        page: int = 1,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get all user preferences with pagination
        
        Args:
            page: Page number (default: 1)
            limit: Items per page (default: 10)
            
        Returns:
            Preferences list with pagination info
        """
        try:
            logger.info(f"Getting user preferences (page {page}, limit {limit})")
            
            url = f"{self.base_url}/user-preferences"
            
            params = {
                "page": page,
                "limit": limit
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Retrieved {len(data.get('preferences', []))} preferences")
                    return {
                        "success": True,
                        "preferences": data.get("preferences", []),
                        "pagination": data.get("pagination", {})
                    }
                else:
                    logger.error(f"Failed to get preferences: {response.status_code}")
                    return {
                        "success": False,
                        "error": response.text,
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            logger.error(f"Error getting user preferences: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_user_preference(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get specific user preference by user_id"""
        try:
            url = f"{self.base_url}/user-preferences/user/{user_id}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "preference": data
                    }
                else:
                    return {
                        "success": False,
                        "error": response.text
                    }
                    
        except Exception as e:
            logger.error(f"Error getting user preference: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def save_memory(
        self,
        user_id: str,
        key: str,
        value: Any,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save data to GetCirclo Memory
        
        Args:
            user_id: User identifier
            key: Memory key
            value: Value to store (will be JSON serialized)
            context: Optional context/namespace
            
        Returns:
            Success status
        """
        try:
            if not self.memory_enabled:
                logger.warning("GetCirclo Memory is disabled")
                return {"success": False, "error": "Memory disabled"}
            
            logger.info(f"Saving memory for user {user_id}: {key}")
            
            url = f"{self.base_url}/memory/save"
            
            payload = {
                "user_id": user_id,
                "key": key,
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
            
            if context:
                payload["context"] = context
                
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Memory saved successfully for {user_id}")
                    return {
                        "success": True,
                        "message": "Memory saved",
                        "user_id": user_id,
                        "key": key
                    }
                else:
                    logger.error(f"Memory save failed: {response.status_code}")
                    return {
                        "success": False,
                        "error": response.text,
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            logger.error(f"Error saving memory to GetCirclo: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_memory(
        self,
        user_id: str,
        key: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve data from GetCirclo Memory
        
        Args:
            user_id: User identifier
            key: Optional specific key (if None, returns all)
            context: Optional context/namespace
            
        Returns:
            Memory data
        """
        try:
            if not self.memory_enabled:
                logger.warning("GetCirclo Memory is disabled")
                return {"success": False, "error": "Memory disabled"}
            
            logger.info(f"Getting memory for user {user_id}")
            
            url = f"{self.base_url}/memory/get"
            
            params = {"user_id": user_id}
            
            if key:
                params["key"] = key
                
            if context:
                params["context"] = context
                
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Memory retrieved for {user_id}")
                    return {
                        "success": True,
                        "data": data.get("data", {}),
                        "user_id": user_id
                    }
                else:
                    logger.error(f"Memory get failed: {response.status_code}")
                    return {
                        "success": False,
                        "error": response.text,
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            logger.error(f"Error getting memory from GetCirclo: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def delete_memory(
        self,
        user_id: str,
        key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delete memory data"""
        try:
            url = f"{self.base_url}/memory/delete"
            
            payload = {"user_id": user_id}
            
            if key:
                payload["key"] = key
                
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return {"success": True, "message": "Memory deleted"}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"Error deleting memory: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def save_user_preference(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save user preferences to GetCirclo Memory"""
        return await self.save_memory(
            user_id=user_id,
            key="preferences",
            value=preferences,
            context="trendscout"
        )
    
    async def get_user_preference(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences from GetCirclo Memory"""
        result = await self.get_memory(
            user_id=user_id,
            key="preferences",
            context="trendscout"
        )
        
        if result.get("success"):
            return result.get("data", {})
        else:
            return {}
    
    async def save_interaction_history(
        self,
        user_id: str,
        interaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save interaction to history"""
        history_result = await self.get_memory(
            user_id=user_id,
            key="history",
            context="trendscout"
        )
        
        history = []
        if history_result.get("success"):
            history = history_result.get("data", {}).get("history", [])
        
        history.append({
            **interaction,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(history) > 50:
            history = history[-50:]
        
        return await self.save_memory(
            user_id=user_id,
            key="history",
            value={"history": history},
            context="trendscout"
        )
    
    async def get_interaction_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get interaction history"""
        result = await self.get_memory(
            user_id=user_id,
            key="history",
            context="trendscout"
        )
        
        if result.get("success"):
            history = result.get("data", {}).get("history", [])
            return history[-limit:]
        else:
            return []
    
    async def create_agent_session(
        self,
        user_id: str,
        agent_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create agent session in GetCirclo"""
        try:
            url = f"{self.base_url}/agent/session"
            
            payload = {
                "user_id": user_id,
                "agent_name": agent_name,
                "timestamp": datetime.now().isoformat()
            }
            
            if metadata:
                payload["metadata"] = metadata
                
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    return {
                        "success": True,
                        "session_id": data.get("session_id"),
                        "agent_name": agent_name
                    }
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"Error creating agent session: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def log_agent_action(
        self,
        session_id: str,
        action: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log agent action to GetCirclo"""
        try:
            url = f"{self.base_url}/agent/log"
            
            payload = {
                "session_id": session_id,
                "action": action,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code in [200, 201]:
                    return {"success": True}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"Error logging agent action: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_whatsapp_message(
        self,
        phone_number: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send WhatsApp message via GetCirclo
        
        Args:
            phone_number: Recipient phone number (international format)
            message: Message text
            
        Returns:
            Send result
        """
        try:
            if not self.whatsapp_enabled:
                logger.warning("GetCirclo WhatsApp is disabled")
                return {"success": False, "error": "WhatsApp disabled"}
            
            logger.info(f"Sending WhatsApp message to {phone_number}")
            
            url = f"{self.base_url}/whatsapp/send"
            
            payload = {
                "phone": phone_number,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"WhatsApp message sent to {phone_number}")
                    return {
                        "success": True,
                        "phone": phone_number,
                        "message_id": response.json().get("message_id")
                    }
                else:
                    logger.error(f"WhatsApp send failed: {response.status_code}")
                    return {
                        "success": False,
                        "error": response.text,
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            logger.error(f"Error sending WhatsApp: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_bulk_whatsapp(
        self,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Send bulk WhatsApp messages
        
        Args:
            messages: List of {"phone": "...", "message": "..."}
            
        Returns:
            Bulk send results
        """
        try:
            logger.info(f"Sending {len(messages)} WhatsApp messages")
            
            results = []
            
            for msg in messages:
                result = await self.send_whatsapp_message(
                    phone_number=msg["phone"],
                    message=msg["message"]
                )
                results.append(result)
                
                await asyncio.sleep(0.5)
            
            success_count = sum(1 for r in results if r.get("success"))
            
            return {
                "success": True,
                "total": len(messages),
                "sent": success_count,
                "failed": len(messages) - success_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error sending bulk WhatsApp: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_post(
        self,
        profile: str,
        media_type: str,
        media_source: str,
        caption: str,
        niche: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a post on Circlo
        
        Args:
            profile: Either "general" or specific profile_id
            media_type: "image" or "video"
            media_source: URL of media from Replicate
            caption: Post caption text (required)
            niche: Niche/sub-niche (required when profile is "general")
            keywords: Optional list of keywords/hashtags
            
        Returns:
            Created post info
        """
        try:
            logger.info(f"Creating post on Circlo (profile: {profile})")
            
            url = f"{self.base_url}/user-preferences/recommend/create-post"
            
            payload = {
                "profile": profile,
                "media_type": media_type,
                "media_source": media_source,
                "caption": caption
            }
            
            if niche:
                payload["niche"] = niche
                
            if keywords:
                payload["keywords"] = keywords
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    data = response.json()
                    logger.info(f"Post created successfully: {data.get('post', {}).get('id')}")
                    return {
                        "success": True,
                        "post": data.get("post", {})
                    }
                else:
                    logger.error(f"Post creation failed: {response.status_code}")
                    return {
                        "success": False,
                        "error": response.text,
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_agent(
        self,
        name: str,
        username: str,
        niche: str,
        avatar_url: str,
        endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register an agent profile on Circlo
        
        Args:
            name: Display name for the agent
            username: Unique handle
            niche: Primary niche the agent represents
            avatar_url: Public image URL for agent's avatar
            endpoint: Optional HTTPS URL for custom agent endpoint
            
        Returns:
            Created agent profile info
        """
        try:
            logger.info(f"Creating agent profile: {username}")
            
            url = f"{self.base_url}/profiles/agent"
            
            payload = {
                "name": name,
                "username": username,
                "niche": niche,
                "avatar_url": avatar_url
            }
            
            if endpoint:
                payload["endpoint"] = endpoint
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    data = response.json()
                    logger.info(f"Agent created successfully: {data.get('id')}")
                    return {
                        "success": True,
                        "agent": data
                    }
                elif response.status_code == 409:
                    logger.error(f"Agent username already exists: {username}")
                    return {
                        "success": False,
                        "error": "Username already exists",
                        "status_code": 409
                    }
                else:
                    logger.error(f"Agent creation failed: {response.status_code}")
                    return {
                        "success": False,
                        "error": response.text,
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check GetCirclo API health"""
        try:
            url = f"{self.base_url}/health"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "status": "healthy",
                        "whatsapp_enabled": self.whatsapp_enabled,
                        "memory_enabled": self.memory_enabled
                    }
                else:
                    return {
                        "success": False,
                        "status": "unhealthy",
                        "error": response.text
                    }
                    
        except Exception as e:
            logger.error(f"GetCirclo health check failed: {str(e)}")
            return {
                "success": False,
                "status": "error",
                "error": str(e)
            }
