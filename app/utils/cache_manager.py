"""
Cache Manager - Simple file-based caching to reduce API calls
"""
import os
import json
import time
import hashlib
import logging
from pathlib import Path
from typing import Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Simple file-based cache manager
    Reduces API calls by caching results
    """
    
    def __init__(self, cache_dir: str = "data/cache", ttl_seconds: int = 3600):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache files
            ttl_seconds: Time-to-live in seconds (default: 1 hour)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds
        
    def _get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Create a unique key from arguments
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, cache_key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Returns None if not found or expired
        """
        try:
            cache_path = self._get_cache_path(cache_key)
            
            if not cache_path.exists():
                return None
            
            # Check if expired
            file_age = time.time() - cache_path.stat().st_mtime
            if file_age > self.ttl_seconds:
                logger.debug(f"Cache expired: {cache_key}")
                cache_path.unlink()  # Delete expired cache
                return None
            
            # Read cached data
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
            
            logger.info(f"Cache hit: {cache_key}")
            return cached_data['value']
            
        except Exception as e:
            logger.warning(f"Cache read error: {str(e)}")
            return None
    
    def set(self, cache_key: str, value: Any) -> bool:
        """
        Save value to cache
        
        Returns True if successful
        """
        try:
            cache_path = self._get_cache_path(cache_key)
            
            cached_data = {
                'value': value,
                'timestamp': time.time()
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cached_data, f, default=str)
            
            logger.info(f"Cache saved: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Cache write error: {str(e)}")
            return False
    
    def clear_expired(self):
        """Clear all expired cache files"""
        try:
            count = 0
            for cache_file in self.cache_dir.glob("*.json"):
                file_age = time.time() - cache_file.stat().st_mtime
                if file_age > self.ttl_seconds:
                    cache_file.unlink()
                    count += 1
            
            if count > 0:
                logger.info(f"Cleared {count} expired cache files")
                
        except Exception as e:
            logger.error(f"Cache cleanup error: {str(e)}")
    
    def clear_all(self):
        """Clear all cache files"""
        try:
            count = 0
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
            
            logger.info(f"Cleared {count} cache files")
            
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")


def cached(ttl_seconds: int = 3600, cache_dir: str = "data/cache"):
    """
    Decorator to cache function results
    
    Usage:
        @cached(ttl_seconds=1800)
        async def expensive_api_call(param1, param2):
            # ... expensive operation
            return result
    """
    def decorator(func: Callable):
        cache = CacheManager(cache_dir=cache_dir, ttl_seconds=ttl_seconds)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._get_cache_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._get_cache_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global cache instance
default_cache = CacheManager(cache_dir="data/cache", ttl_seconds=3600)
