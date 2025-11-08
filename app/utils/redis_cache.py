"""
Redis Cache Manager - Distributed caching with Redis
Faster and more scalable than file-based caching
"""
import redis
import json
import logging
from typing import Any, Optional
import hashlib
from functools import wraps

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisCache:
    """Redis-based cache manager for distributed caching"""
    
    def __init__(self):
        self.redis_url = settings.redis_url
        self.ttl = getattr(settings, 'redis_cache_ttl', 7200)  # 2 hours default
        self.client = None
        self._connect()
        
    def _connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.client.ping()
            logger.info("✅ Connected to Redis successfully")
        except redis.ConnectionError as e:
            logger.error(f"❌ Redis connection failed: {str(e)}")
            logger.warning("⚠️  Falling back to in-memory cache")
            self.client = None
        except Exception as e:
            logger.error(f"❌ Redis setup error: {str(e)}")
            self.client = None
    
    def _get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from parameters"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"trendscout:{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                logger.info(f"✅ Redis cache hit: {key[:40]}...")
                return json.loads(value)
            logger.debug(f"❌ Redis cache miss: {key[:40]}...")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Cache JSON decode error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache"""
        if not self.client:
            return False
        
        try:
            ttl = ttl or self.ttl
            value_json = json.dumps(value, default=str)
            self.client.setex(key, ttl, value_json)
            logger.info(f"💾 Redis cached: {key[:40]}... (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            logger.info(f"🗑️  Deleted from Redis: {key[:40]}...")
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                count = self.client.delete(*keys)
                logger.info(f"🗑️  Cleared {count} keys matching: {pattern}")
                return count
            return 0
        except Exception as e:
            logger.error(f"Redis clear error: {str(e)}")
            return 0
    
    def get_stats(self) -> dict:
        """Get Redis statistics"""
        if not self.client:
            return {
                "status": "disconnected",
                "message": "Redis not available"
            }
        
        try:
            info = self.client.info()
            keyspace = self.client.info('keyspace')
            
            # Calculate cache hit rate
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0
            
            # Get key count
            db_info = keyspace.get('db0', {})
            key_count = db_info.get('keys', 0) if isinstance(db_info, dict) else 0
            
            return {
                "status": "connected",
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "N/A"),
                "total_commands": info.get("total_commands_processed", 0),
                "keyspace_hits": hits,
                "keyspace_misses": misses,
                "hit_rate": f"{hit_rate:.2f}%",
                "total_keys": key_count,
                "uptime_days": info.get("uptime_in_days", 0)
            }
        except Exception as e:
            logger.error(f"Redis stats error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        if not self.client:
            return False
        
        try:
            self.client.ping()
            return True
        except:
            return False


# Global Redis cache instance
redis_cache = RedisCache()


def cached_redis(prefix: str = "cache", ttl: int = 7200):
    """
    Decorator for Redis caching
    
    Usage:
        @cached_redis(prefix="bestsellers", ttl=3600)
        def find_bestsellers(category: str):
            # ... expensive operation
            return results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = redis_cache._get_cache_key(prefix, func.__name__, *args, **kwargs)
            
            # Try cache
            cached_value = redis_cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function
            result = func(*args, **kwargs)
            
            # Cache result
            redis_cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
