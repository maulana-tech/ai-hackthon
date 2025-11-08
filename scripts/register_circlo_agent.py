"""
Register TrendScout AI Agent on GetCirclo Platform

This script creates an agent profile on GetCirclo and wires it to our webhook endpoint.
"""
import asyncio
import httpx
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings

settings = get_settings()

async def register_agent():
    """
    Register TrendScout AI Agent on GetCirclo platform
    
    Creates an agent profile with:
    - Name: TrendScout AI
    - Username: trendscout-ai
    - Niche: E-commerce & Business
    - Webhook: Our server endpoint
    """
    
    # GetCirclo API base URL
    base_url = "https://api.getcirclo.com"
    
    # Agent configuration
    agent_config = {
        "name": "TrendScout AI",
        "username": "trendscout-ai",
        "niche": "E-commerce & Business",
        "avatar_url": "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f50d.png",  # 🔍 emoji
        "endpoint": os.getenv("AGENT_WEBHOOK_URL", "https://your-domain.com/circlo-webhook/hook")
    }
    
    print("=" * 80)
    print("🤖 REGISTERING TRENDSCOUT AI AGENT ON GETCIRCLO")
    print("=" * 80)
    print()
    print(f"Agent Name: {agent_config['name']}")
    print(f"Username: {agent_config['username']}")
    print(f"Niche: {agent_config['niche']}")
    print(f"Webhook URL: {agent_config['endpoint']}")
    print()
    
    # Check if JWT token is available
    jwt_token = settings.getcirclo_jwt_token
    if not jwt_token:
        print("❌ ERROR: GetCirclo JWT token not found!")
        print()
        print("Please set GETCIRCLO_JWT_TOKEN in your .env file")
        print("Contact GetCirclo admin to get your token")
        return False
    
    print(f"✅ JWT Token found: {jwt_token[:20]}...")
    print()
    
    # Check webhook URL
    webhook_url = agent_config['endpoint']
    if "your-domain.com" in webhook_url:
        print("⚠️  WARNING: Webhook URL is not configured!")
        print()
        print("Please set AGENT_WEBHOOK_URL in your environment:")
        print("  export AGENT_WEBHOOK_URL=https://your-production-url.com/circlo-webhook/hook")
        print()
        print("For local testing, use ngrok or similar service:")
        print("  1. Run: ngrok http 8000")
        print("  2. Use the HTTPS URL from ngrok")
        print("  3. Set: export AGENT_WEBHOOK_URL=https://abc123.ngrok.io/circlo-webhook/hook")
        print()
        
        use_anyway = input("Continue with placeholder URL? (y/N): ")
        if use_anyway.lower() != 'y':
            return False
    
    # Register agent via API
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    print("📡 Sending registration request to GetCirclo...")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/api/profiles/agent",
                json=agent_config,
                headers=headers
            )
            
            if response.status_code == 201:
                result = response.json()
                
                print("=" * 80)
                print("✅ AGENT REGISTERED SUCCESSFULLY!")
                print("=" * 80)
                print()
                print(f"Agent ID: {result.get('id')}")
                print(f"Name: {result.get('name')}")
                print(f"Username: {result.get('username')}")
                print(f"Niche: {result.get('niche')}")
                print(f"Endpoint: {result.get('endpoint')}")
                print(f"Is Agent: {result.get('is_agent')}")
                print(f"Created At: {result.get('createdAt')}")
                print()
                print("=" * 80)
                print("🎉 YOUR AGENT IS NOW LIVE ON GETCIRCLO!")
                print("=" * 80)
                print()
                print("Next Steps:")
                print("1. Users can now start conversations with @trendscout-ai")
                print("2. Monitor logs at: logs/server.log")
                print("3. Test the integration with sample queries")
                print()
                print("Sample Queries:")
                print("  • Carikan produk elektronik yang lagi trending")
                print("  • Cari 5 produk fashion terlaris")
                print("  • Tolong carikan supplier tas di Jakarta")
                print()
                
                return True
                
            elif response.status_code == 409:
                print("=" * 80)
                print("⚠️  AGENT ALREADY EXISTS")
                print("=" * 80)
                print()
                print(f"Username '@{agent_config['username']}' is already registered.")
                print()
                print("Options:")
                print("1. Use a different username")
                print("2. Update existing agent configuration")
                print("3. Delete old agent and re-register")
                print()
                return False
                
            elif response.status_code == 400:
                print("=" * 80)
                print("❌ BAD REQUEST")
                print("=" * 80)
                print()
                print("Missing required fields or invalid data.")
                print()
                print(f"Response: {response.text}")
                print()
                return False
                
            else:
                print("=" * 80)
                print(f"❌ REGISTRATION FAILED (Status: {response.status_code})")
                print("=" * 80)
                print()
                print(f"Response: {response.text}")
                print()
                return False
                
    except httpx.TimeoutException:
        print("❌ Request timed out. Please check your internet connection.")
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_webhook():
    """Test if webhook endpoint is accessible"""
    
    webhook_url = os.getenv("AGENT_WEBHOOK_URL", "http://localhost:8000/circlo-webhook/hook")
    
    print()
    print("=" * 80)
    print("🧪 TESTING WEBHOOK ENDPOINT")
    print("=" * 80)
    print()
    print(f"Testing: {webhook_url}")
    print()
    
    # Sample payload
    test_payload = {
        "history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help you today?"}
        ],
        "message": "Carikan produk elektronik terlaris",
        "user": {
            "id": "test-user-123",
            "name": "Test User",
            "preferredKeywords": ["elektronik", "gadget"],
            "preferredNiches": ["Tech"]
        },
        "profile": {
            "id": "agent-123",
            "name": "TrendScout AI",
            "niche": "E-commerce"
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                webhook_url,
                json=test_payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ WEBHOOK IS WORKING!")
                print()
                print("Response:")
                print(f"  {result.get('response', result.get('message'))[:200]}...")
                print()
                return True
            else:
                print(f"❌ Webhook returned status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False
                
    except httpx.ConnectError:
        print("❌ Cannot connect to webhook endpoint.")
        print()
        print("Make sure your server is running:")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False
        
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")
        return False

async def main():
    """Main function"""
    
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "GETCIRCLO AGENT REGISTRATION" + " " * 30 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # Test webhook first (if local)
    webhook_url = os.getenv("AGENT_WEBHOOK_URL", "http://localhost:8000/circlo-webhook/hook")
    if "localhost" in webhook_url or "127.0.0.1" in webhook_url:
        webhook_ok = await test_webhook()
        if not webhook_ok:
            print()
            print("⚠️  Webhook test failed. Please fix webhook issues before registering.")
            print()
            return
    
    # Register agent
    success = await register_agent()
    
    if success:
        print()
        print("🎉 Setup complete! Your agent is ready to receive conversations.")
        print()
    else:
        print()
        print("❌ Registration failed. Please check the errors above.")
        print()

if __name__ == "__main__":
    asyncio.run(main())
