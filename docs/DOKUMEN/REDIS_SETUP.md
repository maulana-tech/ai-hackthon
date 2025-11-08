# Redis Setup Guide

Complete guide for setting up Redis for distributed caching in TrendScout AI.

---

## 🎯 Why Redis?

### Current: File-Based Cache
```
✅ Simple
✅ Works locally
❌ Not scalable
❌ Not distributed
❌ Slower than Redis
```

### With Redis
```
✅ Fast (in-memory)
✅ Distributed (multiple servers)
✅ Persistent (optional)
✅ Production-ready
✅ Industry standard
```

---

## 📋 Installation

### Option 1: macOS (Homebrew)

```bash
# Install Redis
brew install redis

# Start Redis server
brew services start redis

# Or start manually
redis-server

# Verify
redis-cli ping
# Should return: PONG
```



### Option 4: Cloud Redis

**Upstash** (Free tier available):
```bash
# Get connection string from:
https://upstash.com/

# Example:
REDIS_URL=redis://default:xxxxx@us1-redis.upstash.io:6379
```

**Redis Cloud** (Free tier):
```bash
# Get from:
https://redis.com/try-free/

# Connection string:
REDIS_URL=redis://user:password@host:port
```

---

## 🔧 Configuration

### 1. Install Python Redis Client

```bash
# Activate virtual environment
source .venv/bin/activate

# Install redis-py
pip install redis aioredis

# Update requirements.txt
pip freeze | grep redis >> requirements.txt
```

### 2. Update .env

```bash
# Local Redis (default)
REDIS_URL=redis://localhost:6379/0

# Or Cloud Redis
REDIS_URL=redis://default:password@host:port/0

# Redis settings
REDIS_CACHE_TTL=7200  # 2 hours in seconds
REDIS_MAX_CONNECTIONS=50
```

### 3. Verify Connection

```bash
# Test Redis connection
python scripts/test_redis_connection.py
```

---

## 💻 Implementation

### Create Redis Cache Manager

File: `app/utils/redis_cache.py`

```python
"""
Redis Cache Manager - Distributed caching with Redis
"""
import redis.asyncio as redis
import json
import logging
from typing import Any, Optional
import hashlib

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisCache:
    """Redis-based cache manager"""
    
    def __init__(self):
        self.redis_url = settings.redis_url
        self.ttl = getattr(settings, 'redis_cache_ttl', 7200)
        self.client = None
        
    async def connect(self):
        """Connect to Redis"""
        if not self.client:
            try:
                self.client = await redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=50
                )
                await self.client.ping()
                logger.info("✅ Connected to Redis")
            except Exception as e:
                logger.error(f"❌ Redis connection failed: {str(e)}")
                self.client = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")
    
    def _get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            await self.connect()
        
        if not self.client:
            return None
        
        try:
            value = await self.client.get(key)
            if value:
                logger.info(f"✅ Cache hit: {key[:30]}...")
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        if not self.client:
            await self.connect()
        
        if not self.client:
            return False
        
        try:
            ttl = ttl or self.ttl
            value_json = json.dumps(value, default=str)
            await self.client.setex(key, ttl, value_json)
            logger.info(f"💾 Cached: {key[:30]}... (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete from cache"""
        if not self.client:
            return False
        
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    async def clear_all(self) -> bool:
        """Clear all cache (use carefully!)"""
        if not self.client:
            return False
        
        try:
            await self.client.flushdb()
            logger.info("🗑️  All cache cleared")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return False
    
    async def get_stats(self) -> dict:
        """Get Redis statistics"""
        if not self.client:
            return {}
        
        try:
            info = await self.client.info()
            return {
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory_human"),
                "total_commands": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "uptime_days": info.get("uptime_in_days")
            }
        except Exception as e:
            logger.error(f"Stats error: {str(e)}")
            return {}


# Global instance
redis_cache = RedisCache()


# Decorator for automatic caching
def cached_redis(prefix: str = "cache", ttl: int = 7200):
    """
    Decorator for Redis caching
    
    Usage:
        @cached_redis(prefix="bestsellers", ttl=3600)
        async def find_bestsellers(category: str):
            # ... expensive operation
            return results
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = redis_cache._get_cache_key(prefix, *args, **kwargs)
            
            # Try cache
            cached_value = await redis_cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Cache result
            await redis_cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
```

---

## 🔄 Update Firecrawl Client

Replace file-based cache with Redis:

```python
# app/integrations/firecrawl_client.py

from app.utils.redis_cache import redis_cache

class FirecrawlClient:
    def __init__(self):
        self.client = FirecrawlApp(api_key=settings.firecrawl_api_key)
        self.cache = redis_cache  # Use Redis instead of file cache
    
    async def scrape(self, url: str, **kwargs):
        # Generate cache key
        cache_key = self.cache._get_cache_key("firecrawl:scrape", url, **kwargs)
        
        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Scrape
        result = self.client.scrape_url(url, **kwargs)
        
        # Cache result
        await self.cache.set(cache_key, result, ttl=7200)
        
        return result
```

---

## 🧪 Testing

### Create Test Script

File: `scripts/test_redis_connection.py`

```python
import asyncio
from app.utils.redis_cache import redis_cache

async def test_redis():
    print("🧪 Testing Redis Connection")
    print("=" * 50)
    
    # Connect
    await redis_cache.connect()
    
    if not redis_cache.client:
        print("❌ Redis not available")
        return
    
    # Test set/get
    print("\n1. Testing SET/GET:")
    await redis_cache.set("test_key", {"hello": "world"}, ttl=60)
    value = await redis_cache.get("test_key")
    print(f"   Value: {value}")
    assert value == {"hello": "world"}, "Value mismatch"
    print("   ✅ SET/GET working")
    
    # Test stats
    print("\n2. Redis Stats:")
    stats = await redis_cache.get_stats()
    for key, val in stats.items():
        print(f"   {key}: {val}")
    
    # Cleanup
    await redis_cache.delete("test_key")
    await redis_cache.disconnect()
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_redis())
```

Run:
```bash
python scripts/test_redis_connection.py
```

---

## 📊 Monitoring

### Redis CLI Commands

```bash
# Connect to Redis
redis-cli

# Check keys
KEYS *

# Get value
GET key_name

# Check memory
INFO memory

# Monitor real-time
MONITOR

# Get stats
INFO stats
```

### Application Monitoring

```python
# Add endpoint to check Redis health
@app.get("/api/cache/stats")
async def cache_stats():
    stats = await redis_cache.get_stats()
    return {
        "redis": "connected" if redis_cache.client else "disconnected",
        "stats": stats
    }
```

---

## 🚀 Deployment

### Production Redis

**Option 1: Self-Hosted**
```bash
# Install on production server
sudo apt install redis-server

# Configure redis.conf
sudo nano /etc/redis/redis.conf

# Set password
requirepass your_strong_password

# Bind to internal IP (not public)
bind 127.0.0.1

# Restart
sudo systemctl restart redis-server
```

**Option 2: Managed Redis (Recommended)**

**Upstash** (Recommended for serverless):
- Free tier available
- Global replication
- REST API fallback
- Setup: https://upstash.com

**Redis Cloud**:
- Free 30MB
- Multi-cloud
- Setup: https://redis.com

**AWS ElastiCache**:
- Enterprise-grade
- Auto-scaling
- Setup via AWS Console

---

## ⚡ Performance Comparison

### File-Based Cache
```
Write: ~10ms
Read: ~5ms
Scalability: Single server only
Concurrency: Limited
```

### Redis Cache
```
Write: <1ms
Read: <0.5ms
Scalability: Distributed
Concurrency: Thousands/sec
```

### Improvement
```
Speed: 10-20x faster
Scalability: Infinite (with cluster)
Reliability: Much better
```

---

## 🔐 Security

### Secure Redis

```bash
# redis.conf settings

# 1. Set strong password
requirepass YourVeryStrongPassword123!

# 2. Bind to localhost only (if same server)
bind 127.0.0.1

# 3. Or use firewall (if separate server)
bind 0.0.0.0
# + Configure firewall to allow only your app server

# 4. Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""

# 5. Enable persistence (optional)
save 900 1
save 300 10
save 60 10000
```

---

## ✅ Setup Checklist

### Local Development
- [ ] Install Redis (`brew install redis`)
- [ ] Start Redis (`brew services start redis`)
- [ ] Test connection (`redis-cli ping`)
- [ ] Install redis-py (`pip install redis aioredis`)
- [ ] Create RedisCache class
- [ ] Test with script
- [ ] Update Firecrawl client
- [ ] Verify caching works

### Production
- [ ] Choose Redis hosting (Upstash/Cloud/Self-hosted)
- [ ] Get connection URL
- [ ] Update .env with REDIS_URL
- [ ] Configure security (password, firewall)
- [ ] Set up monitoring
- [ ] Test in production
- [ ] Monitor performance

---

## 🎯 Next Steps After Setup

1. **Replace File Cache**: Update all cache usages
2. **Add Redis Stats Endpoint**: Monitor cache health
3. **Optimize TTL**: Fine-tune cache duration
4. **Add Cache Warming**: Pre-cache popular queries
5. **Monitor Hit Rate**: Aim for >80% hit rate

---

## 📚 Resources

- **Redis Docs**: https://redis.io/docs/
- **redis-py Docs**: https://redis-py.readthedocs.io/
- **Upstash**: https://upstash.com/
- **Redis Cloud**: https://redis.com/

---

**Ready to implement? Let's do it!** 🚀
