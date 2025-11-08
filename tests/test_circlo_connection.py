"""
Test GetCirclo API connection
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.integrations.getcirclo_client import GetCircloClient
from app.config import get_settings

async def test_circlo_connection():
    """Test basic GetCirclo API connection"""
    
    print("=" * 70)
    print("TESTING GETCIRCLO API CONNECTION")
    print("=" * 70)
    print()
    
    settings = get_settings()
    
    # Check if credentials are configured
    if not settings.getcirclo_jwt_token and not settings.getcirclo_api_key:
        print("❌ ERROR: No GetCirclo credentials configured")
        print("   Please set GETCIRCLO_JWT_TOKEN or GETCIRCLO_API_KEY in .env")
        return
    
    if settings.getcirclo_jwt_token:
        print(f"✅ Using JWT Token: {settings.getcirclo_jwt_token[:20]}...")
    else:
        print(f"✅ Using API Key: {settings.getcirclo_api_key[:20]}...")
    
    print()
    
    # Initialize client
    client = GetCircloClient()
    
    # Test 1: Get user preferences
    print("Test 1: Get User Preferences")
    print("-" * 70)
    
    try:
        result = await client.get_all_user_preferences(page=1, limit=5)
        
        if result.get('success'):
            print(f"✅ SUCCESS: Retrieved user preferences")
            preferences = result.get('preferences', [])
            print(f"   Found {len(preferences)} preferences")
            
            if preferences:
                print(f"\n   Sample preference:")
                pref = preferences[0]
                print(f"   - User ID: {pref.get('user_id', 'N/A')}")
                print(f"   - Niche: {pref.get('niche', 'N/A')}")
                print(f"   - Budget: {pref.get('budget_min', 'N/A')} - {pref.get('budget_max', 'N/A')}")
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
            if result.get('status_code'):
                print(f"   Status code: {result['status_code']}")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 2: Get agent profile
    print("Test 2: Get Agent Profile")
    print("-" * 70)
    
    try:
        result = await client.get_agent_profile()
        
        if result.get('success'):
            print(f"✅ SUCCESS: Retrieved agent profile")
            profile = result.get('profile', {})
            print(f"   Agent Name: {profile.get('name', 'N/A')}")
            print(f"   Agent Type: {profile.get('type', 'N/A')}")
            print(f"   Status: {profile.get('status', 'N/A')}")
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print()
    
    # Test 3: Create a test preference
    print("Test 3: Create Test User Preference")
    print("-" * 70)
    
    try:
        test_user_id = "test_user_123"
        test_preferences = {
            "niche": "fashion",
            "budget_min": 100000,
            "budget_max": 500000,
            "preferred_location": "Jakarta",
            "preferred_marketplace": ["tokopedia", "shopee"]
        }
        
        result = await client.save_user_preference(
            user_id=test_user_id,
            preferences=test_preferences
        )
        
        if result.get('success'):
            print(f"✅ SUCCESS: Created test preference for {test_user_id}")
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print()
    
    # Test 4: Check WhatsApp integration
    print("Test 4: Check WhatsApp Integration")
    print("-" * 70)
    
    if settings.getcirclo_whatsapp_enabled:
        print(f"✅ WhatsApp integration: ENABLED")
        print(f"   Ready to send messages via GetCirclo WhatsApp API")
    else:
        print(f"⚠️  WhatsApp integration: DISABLED")
        print(f"   Set GETCIRCLO_WHATSAPP_ENABLED=true in .env to enable")
    
    print()
    
    # Summary
    print("=" * 70)
    print("CONNECTION TEST SUMMARY")
    print("=" * 70)
    print()
    print(f"GetCirclo API Base: {client.base_url}")
    print(f"Authentication: {'JWT Token' if settings.getcirclo_jwt_token else 'API Key'}")
    print(f"WhatsApp Enabled: {settings.getcirclo_whatsapp_enabled}")
    print(f"Memory Enabled: {settings.getcirclo_memory_enabled}")
    print()
    print("✅ Connection test completed!")

if __name__ == "__main__":
    asyncio.run(test_circlo_connection())
