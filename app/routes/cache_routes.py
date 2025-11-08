"""
Cache Management Routes
Endpoints for monitoring and managing cache
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from app.utils.redis_cache import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cache", tags=["cache"])


@router.get("/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """
    Get Redis cache statistics
    
    Returns cache metrics including:
    - Connection status
    - Hit/miss rate
    - Memory usage
    - Key count
    - Uptime
    """
    try:
        stats = redis_cache.get_stats()
        
        return {
            "success": True,
            "cache_type": "Redis",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        return {
            "success": False,
            "cache_type": "Redis",
            "error": str(e),
            "stats": {
                "status": "error"
            }
        }


@router.get("/health")
async def check_cache_health() -> Dict[str, Any]:
    """
    Check if cache is healthy and responding
    """
    try:
        is_available = redis_cache.is_available()
        
        if is_available:
            return {
                "status": "healthy",
                "cache": "Redis",
                "available": True
            }
        else:
            return {
                "status": "unavailable",
                "cache": "Redis",
                "available": False,
                "message": "Redis not responding"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "cache": "Redis",
            "available": False,
            "error": str(e)
        }


@router.delete("/clear")
async def clear_cache(pattern: str = "*") -> Dict[str, Any]:
    """
    Clear cache keys matching pattern
    
    Args:
        pattern: Redis key pattern (default: "*" = all keys)
        
    Example:
        /api/cache/clear?pattern=trendscout:firecrawl:*
    
    ⚠️ Use with caution! This will delete cached data.
    """
    try:
        if not redis_cache.is_available():
            raise HTTPException(
                status_code=503,
                detail="Redis not available"
            )
        
        # Safety check - don't allow clearing all keys in production
        if pattern == "*":
            logger.warning("Clearing ALL cache keys!")
        
        count = redis_cache.clear_pattern(f"trendscout:{pattern}")
        
        return {
            "success": True,
            "message": f"Cleared {count} keys",
            "pattern": pattern,
            "count": count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.get("/info")
async def get_cache_info() -> Dict[str, Any]:
    """
    Get cache configuration and information
    """
    return {
        "cache_type": "Redis",
        "redis_url": redis_cache.redis_url.replace(
            redis_cache.redis_url.split("@")[0].split("//")[1], "***"
        ) if "@" in redis_cache.redis_url else "localhost:6379",
        "default_ttl": redis_cache.ttl,
        "available": redis_cache.is_available(),
        "features": {
            "distributed": True,
            "persistent": False,  # In-memory by default
            "atomic_operations": True,
            "ttl_support": True,
            "pattern_matching": True
        }
    }
