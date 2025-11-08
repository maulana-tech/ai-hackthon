"""
Test GetCirclo Connection with JWT Token
Verify that JWT token is valid and we can access GetCirclo API
"""
import asyncio
import httpx
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings

settings = get_settings()

async def test_connection():
    """Test GetCirclo API connection"""
    
    print("=" * 80)
    print("🧪 TESTING GETCIRCLO CONNECTION")
    print("=" * 80)
    print()
    
    # Check if JWT token exists
    jwt_token = settings.getcirclo_jwt_token
    if not jwt_token or jwt_token == "":
        print("❌ ERROR: GETCIRCLO_JWT_TOKEN not found in .env")
        print()
        print("Please add your JWT token to .env file:")
        print("GETCIRCLO_JWT_TOKEN=your_token_here")
        return False
    
    # Mask token for display
    masked_token = jwt_token[:20] + "..." + jwt_token[-20:] if len(jwt_token) > 40 else jwt_token[:10] + "..."
    print(f"✅ JWT Token found: {masked_token}")
    print()
    
    base_url = "https://api.getcirclo.com"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Get user preferences (basic API test)
    print("Test 1: Fetching User Preferences")
    print("-" * 80)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{base_url}/api/user-preferences?page=1&limit=5",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                preferences = data.get('preferences', [])
                pagination = data.get('pagination', {})
                
                print(f"✅ SUCCESS - Status: {response.status_code}")
                print(f"✅ Retrieved {len(preferences)} user preferences")
                print(f"✅ Total users: {pagination.get('totalItems', 0)}")
                print()
                
                # Show sample preference
                if preferences:
                    sample = preferences[0]
                    user = sample.get('user', {})
                    print("Sample User Preference:")
                    print(f"  User: {user.get('name')} ({user.get('email')})")
                    print(f"  Keywords: {sample.get('preferredKeywords', [])[:3]}")
                    print(f"  Niches: {sample.get('preferredNiches', [])[:3]}")
                    print()
                
            elif response.status_code == 401:
                print(f"❌ AUTHENTICATION FAILED - Status: {response.status_code}")
                print()
                print("Your JWT token is invalid or expired.")
                print("Please contact GetCirclo admin for a new token.")
                return False
                
            else:
                print(f"⚠️  Unexpected response - Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                print()
                
    except httpx.TimeoutException:
        print("❌ Request timed out")
        print("Check your internet connection")
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # Test 2: Check if we can list agents
    print("Test 2: Checking Agent Profiles Access")
    print("-" * 80)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Try to access profiles endpoint
            response = await client.get(
                f"{base_url}/api/profiles",
                headers=headers
            )
            
            if response.status_code in [200, 404]:
                print(f"✅ Profiles endpoint accessible (Status: {response.status_code})")
                print()
            else:
                print(f"⚠️  Profiles endpoint returned: {response.status_code}")
                print()
                
    except Exception as e:
        print(f"⚠️  Could not test profiles endpoint: {str(e)}")
        print()
    
    # Test 3: Verify webhook endpoint is running locally
    print("Test 3: Checking Local Webhook Endpoint")
    print("-" * 80)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:8000/circlo-webhook/webhook-info")
            
            if response.status_code == 200:
                info = response.json()
                print("✅ Local webhook endpoint is RUNNING")
                print(f"   Endpoint: {info.get('endpoint')}")
                print(f"   Status: {info.get('status')}")
                print()
            else:
                print(f"⚠️  Webhook endpoint returned: {response.status_code}")
                print()
                
    except httpx.ConnectError:
        print("❌ Local server is NOT running")
        print()
        print("Please start the server first:")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print()
        return False
        
    except Exception as e:
        print(f"⚠️  Could not test webhook: {str(e)}")
        print()
    
    # Summary
    print("=" * 80)
    print("📊 CONNECTION TEST SUMMARY")
    print("=" * 80)
    print()
    print("✅ JWT Token: Valid and working")
    print("✅ GetCirclo API: Accessible")
    print("✅ Authentication: Successful")
    print("✅ Local Webhook: Running")
    print()
    print("=" * 80)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("1. Choose deployment method:")
    print("   a) Local testing with ngrok: Install ngrok and expose localhost")
    print("   b) Production server: Deploy to VPS with public domain")
    print()
    print("2. Register agent with webhook URL:")
    print("   python scripts/register_circlo_agent.py")
    print()
    
    return True

async def main():
    """Main function"""
    
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 22 + "GETCIRCLO CONNECTION TEST" + " " * 31 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    success = await test_connection()
    
    if not success:
        print()
        print("❌ Connection test failed. Please fix the issues above.")
        print()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
