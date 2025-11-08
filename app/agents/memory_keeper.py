import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import asyncio

from app.models.schemas import UserPreference, FinalReport
from app.config import get_settings
from app.integrations.getcirclo_client import GetCircloClient

logger = logging.getLogger(__name__)
settings = get_settings()

class MemoryKeeperAgent:
    """Agent to manage user preferences and interaction history"""
    
    def __init__(self):
        self.name = "Memory Keeper Agent"
        self.getcirclo = GetCircloClient()
        self.use_getcirclo_memory = settings.getcirclo_memory_enabled
        self.data_dir = Path("./data/memory")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    async def save_preference(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """Save user preferences"""
        try:
            logger.info(f"Saving preferences for user: {user_id}")
            
            pref = UserPreference(
                user_id=user_id,
                **preferences
            )
            
            if self.use_getcirclo_memory:
                result = await self.getcirclo.save_user_preference(
                    user_id=user_id,
                    preferences=pref.model_dump()
                )
                
                if result.get("success"):
                    logger.info(f"Preferences saved to GetCirclo for user: {user_id}")
                    return True
            
            pref_file = self.data_dir / f"{user_id}_preferences.json"
            
            async with asyncio.Lock():
                with open(pref_file, 'w') as f:
                    json.dump(pref.model_dump(), f, indent=2)
                    
            logger.info(f"Preferences saved locally for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving preferences: {str(e)}")
            return False
            
    async def get_preference(self, user_id: str) -> Optional[UserPreference]:
        """Get user preferences"""
        try:
            if self.use_getcirclo_memory:
                data = await self.getcirclo.get_user_preference(user_id)
                
                if data:
                    return UserPreference(**data)
            
            pref_file = self.data_dir / f"{user_id}_preferences.json"
            
            if not pref_file.exists():
                return None
                
            with open(pref_file, 'r') as f:
                data = json.load(f)
                
            return UserPreference(**data)
            
        except Exception as e:
            logger.error(f"Error getting preferences: {str(e)}")
            return None
            
    async def save_interaction(
        self,
        user_id: str,
        report: FinalReport
    ) -> bool:
        """Save interaction history"""
        try:
            logger.info(f"Saving interaction for user: {user_id}")
            
            interaction = {
                "job_id": report.job_id,
                "query": report.query,
                "timestamp": report.created_at.isoformat(),
                "products_count": len(report.trending_products),
                "suppliers_count": len(report.suppliers),
                "summary": report.summary
            }
            
            if self.use_getcirclo_memory:
                result = await self.getcirclo.save_interaction_history(
                    user_id=user_id,
                    interaction=interaction
                )
                
                if result.get("success"):
                    logger.info(f"Interaction saved to GetCirclo for user: {user_id}")
                    return True
            
            history_file = self.data_dir / f"{user_id}_history.json"
            
            history = []
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history = json.load(f)
                    
            history.append(interaction)
            
            if len(history) > 50:
                history = history[-50:]
                
            async with asyncio.Lock():
                with open(history_file, 'w') as f:
                    json.dump(history, f, indent=2)
                    
            logger.info(f"Interaction saved locally for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving interaction: {str(e)}")
            return False
            
    async def get_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get user interaction history"""
        try:
            if self.use_getcirclo_memory:
                history = await self.getcirclo.get_interaction_history(
                    user_id=user_id,
                    limit=limit
                )
                
                if history:
                    return history
            
            history_file = self.data_dir / f"{user_id}_history.json"
            
            if not history_file.exists():
                return []
                
            with open(history_file, 'r') as f:
                history = json.load(f)
                
            return history[-limit:]
            
        except Exception as e:
            logger.error(f"Error getting history: {str(e)}")
            return []
            
    async def update_supplier_rating(
        self,
        user_id: str,
        supplier_id: str,
        rating: float,
        feedback: Optional[str] = None
    ) -> bool:
        """Update supplier rating based on user feedback"""
        try:
            logger.info(f"Updating supplier rating: {supplier_id}")
            
            ratings_file = self.data_dir / f"{user_id}_supplier_ratings.json"
            
            ratings = {}
            if ratings_file.exists():
                with open(ratings_file, 'r') as f:
                    ratings = json.load(f)
                    
            ratings[supplier_id] = {
                "rating": rating,
                "feedback": feedback,
                "updated_at": datetime.now().isoformat()
            }
            
            async with asyncio.Lock():
                with open(ratings_file, 'w') as f:
                    json.dump(ratings, f, indent=2)
                    
            return True
            
        except Exception as e:
            logger.error(f"Error updating supplier rating: {str(e)}")
            return False
            
    async def get_supplier_ratings(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get all supplier ratings for user"""
        try:
            ratings_file = self.data_dir / f"{user_id}_supplier_ratings.json"
            
            if not ratings_file.exists():
                return {}
                
            with open(ratings_file, 'r') as f:
                ratings = json.load(f)
                
            return ratings
            
        except Exception as e:
            logger.error(f"Error getting supplier ratings: {str(e)}")
            return {}
            
    async def learn_from_feedback(
        self,
        user_id: str,
        job_id: str,
        feedback: Dict[str, Any]
    ) -> bool:
        """Learn from user feedback to improve recommendations"""
        try:
            logger.info(f"Learning from feedback: {job_id}")
            
            feedback_file = self.data_dir / f"{user_id}_feedback.json"
            
            feedbacks = []
            if feedback_file.exists():
                with open(feedback_file, 'r') as f:
                    feedbacks = json.load(f)
                    
            feedbacks.append({
                "job_id": job_id,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            })
            
            async with asyncio.Lock():
                with open(feedback_file, 'w') as f:
                    json.dump(feedbacks, f, indent=2)
                    
            preferences = await self.get_preference(user_id)
            if preferences:
                if feedback.get('preferred_location'):
                    preferences.preferred_location = feedback['preferred_location']
                if feedback.get('budget_range'):
                    preferences.budget_min = feedback['budget_range'][0]
                    preferences.budget_max = feedback['budget_range'][1]
                    
                await self.save_preference(user_id, preferences.model_dump())
                
            return True
            
        except Exception as e:
            logger.error(f"Error learning from feedback: {str(e)}")
            return False
            
    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about user behavior and preferences"""
        try:
            history = await self.get_history(user_id, limit=50)
            preferences = await self.get_preference(user_id)
            ratings = await self.get_supplier_ratings(user_id)
            
            insights = {
                "total_queries": len(history),
                "preferences": preferences.model_dump() if preferences else None,
                "favorite_categories": self._analyze_categories(history),
                "preferred_suppliers": self._analyze_suppliers(ratings),
                "average_order_size": self._analyze_order_size(history)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting user insights: {str(e)}")
            return {}
            
    def _analyze_categories(self, history: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze most searched categories"""
        categories = {}
        for item in history:
            query = item.get('query', '').lower()
            if query:
                categories[query] = categories.get(query, 0) + 1
        return dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5])
        
    def _analyze_suppliers(self, ratings: Dict[str, Any]) -> List[str]:
        """Analyze preferred suppliers"""
        sorted_suppliers = sorted(
            ratings.items(),
            key=lambda x: x[1].get('rating', 0),
            reverse=True
        )
        return [s[0] for s in sorted_suppliers[:5]]
        
    def _analyze_order_size(self, history: List[Dict[str, Any]]) -> float:
        """Analyze average order size"""
        return 0.0
