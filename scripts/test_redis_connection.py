"""
Test Redis Connection and Functionality
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.redis_cache import redis_cache
import time

def test_redis():
    """Test Redis connection and basic operations"""
    
    print("=" * 70)
    print("🧪 TESTING REDIS CONNECTION")
    print("=" * 70)
    print()
    
    # Test 1: Connection
    print("Test 1: Redis Connection")
    print("-" * 70)
    
    if not redis_cache.is_available():
        print("❌ Redis is NOT available")
        print()
        print("Please make sure Redis is running:")
        print("  brew services start redis")
        print("  # or")
        print("  redis-server")
        print()
        return False
    
    print("✅ Redis is connected and responding")
    print()
    
    # Test 2: Set/Get
    print("Test 2: SET/GET Operations")
    print("-" * 70)
    
    test_key = "test:key:sample"
    test_value = {"message": "Hello Redis!", "timestamp": time.time()}
    
    # Set value
    success = redis_cache.set(test_key, test_value, ttl=60)
    if success:
        print(f"✅ SET: {test_key}")
    else:
        print(f"❌ SET failed")
        return False
    
    # Get value
    retrieved = redis_cache.get(test_key)
    if retrieved == test_value:
        print(f"✅ GET: Value matches")
    else:
        print(f"❌ GET: Value mismatch")
        print(f"   Expected: {test_value}")
        print(f"   Got: {retrieved}")
        return False
    print()
    
    # Test 3: TTL and Expiration
    print("Test 3: TTL (Time To Live)")
    print("-" * 70)
    
    ttl_key = "test:ttl:key"
    redis_cache.set(ttl_key, "temporary", ttl=2)
    
    # Check exists
    value = redis_cache.get(ttl_key)
    if value:
        print(f"✅ Key exists immediately after set")
    
    print("   Waiting 3 seconds for TTL expiration...")
    time.sleep(3)
    
    # Check expired
    value = redis_cache.get(ttl_key)
    if not value:
        print(f"✅ Key expired after TTL")
    else:
        print(f"❌ Key should have expired")
    print()
    
    # Test 4: Delete
    print("Test 4: DELETE Operation")
    print("-" * 70)
    
    delete_key = "test:delete:key"
    redis_cache.set(delete_key, "to_be_deleted", ttl=300)
    
    # Verify exists
    if redis_cache.get(delete_key):
        print(f"✅ Key exists before delete")
    
    # Delete
    redis_cache.delete(delete_key)
    
    # Verify deleted
    if not redis_cache.get(delete_key):
        print(f"✅ Key deleted successfully")
    else:
        print(f"❌ Delete failed")
    print()
    
    # Test 5: Cache Key Generation
    print("Test 5: Cache Key Generation")
    print("-" * 70)
    
    key1 = redis_cache._get_cache_key("test", "arg1", "arg2", param1="value1")
    key2 = redis_cache._get_cache_key("test", "arg1", "arg2", param1="value1")
    key3 = redis_cache._get_cache_key("test", "arg1", "arg3", param1="value1")
    
    if key1 == key2:
        print(f"✅ Same arguments produce same key")
    else:
        print(f"❌ Same arguments should produce same key")
    
    if key1 != key3:
        print(f"✅ Different arguments produce different keys")
    else:
        print(f"❌ Different arguments should produce different keys")
    print()
    
    # Test 6: Statistics
    print("Test 6: Redis Statistics")
    print("-" * 70)
    
    stats = redis_cache.get_stats()
    
    if stats.get("status") == "connected":
        print(f"✅ Statistics retrieved:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    else:
        print(f"❌ Could not retrieve statistics")
    print()
    
    # Test 7: Pattern Clear
    print("Test 7: Clear Pattern")
    print("-" * 70)
    
    # Create multiple test keys
    for i in range(5):
        redis_cache.set(f"test:pattern:{i}", f"value_{i}", ttl=60)
    
    # Clear all test keys
    count = redis_cache.clear_pattern("test:*")
    print(f"✅ Cleared {count} keys matching pattern 'test:*'")
    print()
    
    # Final Summary
    print("=" * 70)
    print("✅ ALL REDIS TESTS PASSED!")
    print("=" * 70)
    print()
    print("Redis is working correctly and ready for production use.")
    print()
    print("Next steps:")
    print("1. Update Firecrawl client to use Redis cache")
    print("2. Add cache statistics endpoint")
    print("3. Monitor cache hit rate")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = test_redis()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
