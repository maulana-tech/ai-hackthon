#!/usr/bin/env python3
"""
Setup script to register TrendScout agents on Circlo platform

This script creates agent profiles on Circlo and configures
custom endpoints for conversation handling.
"""

import asyncio
import logging
from app.integrations.getcirclo_client import GetCircloClient
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Agent configurations
AGENTS = [
    {
        "name": "TrendScout Super Agent",
        "username": "trendscout-super",
        "niche": "E-commerce & Business",
        "avatar_url": "https://cdn.getcirclo.com/avatars/trendscout-super.png",
        "endpoint": f"https://your-domain.com/api/circlo/circlo-hook",
        "description": "Main orchestrator agent for TrendScout platform"
    },
    {
        "name": "TrendScout Analyst",
        "username": "trendscout-analyst",
        "niche": "Market Research",
        "avatar_url": "https://cdn.getcirclo.com/avatars/trendscout-analyst.png",
        "endpoint": f"https://your-domain.com/api/circlo/circlo-hook",
        "description": "Analyzes global product trends and market insights"
    },
    {
        "name": "TrendScout Supplier Connector",
        "username": "trendscout-supplier",
        "niche": "Supply Chain",
        "avatar_url": "https://cdn.getcirclo.com/avatars/trendscout-supplier.png",
        "endpoint": f"https://your-domain.com/api/circlo/circlo-hook",
        "description": "Connects businesses with Indonesian suppliers"
    },
    {
        "name": "TrendScout Marketing Bot",
        "username": "trendscout-marketing",
        "niche": "Digital Marketing",
        "avatar_url": "https://cdn.getcirclo.com/avatars/trendscout-marketing.png",
        "endpoint": f"https://your-domain.com/api/circlo/circlo-hook",
        "description": "Automates marketing campaigns and content creation"
    }
]


async def register_agent(client: GetCircloClient, agent_config: dict):
    """Register a single agent on Circlo"""
    logger.info(f"Registering agent: {agent_config['name']}")
    
    result = await client.create_agent(
        name=agent_config["name"],
        username=agent_config["username"],
        niche=agent_config["niche"],
        avatar_url=agent_config["avatar_url"],
        endpoint=agent_config.get("endpoint")
    )
    
    if result.get("success"):
        agent_data = result.get("agent", {})
        logger.info(f"✅ Successfully registered: {agent_config['name']}")
        logger.info(f"   Agent ID: {agent_data.get('id')}")
        logger.info(f"   Username: {agent_data.get('username')}")
        logger.info(f"   Endpoint: {agent_data.get('endpoint')}")
        return {
            "success": True,
            "agent": agent_config['name'],
            "data": agent_data
        }
    else:
        error = result.get("error", "Unknown error")
        if result.get("status_code") == 409:
            logger.warning(f"⚠️  Agent already exists: {agent_config['name']}")
            return {
                "success": False,
                "agent": agent_config['name'],
                "error": "Already exists"
            }
        else:
            logger.error(f"❌ Failed to register: {agent_config['name']}")
            logger.error(f"   Error: {error}")
            return {
                "success": False,
                "agent": agent_config['name'],
                "error": error
            }


async def setup_all_agents():
    """Register all TrendScout agents on Circlo"""
    logger.info("=" * 60)
    logger.info("TrendScout Circlo Agents Setup")
    logger.info("=" * 60)
    
    client = GetCircloClient()
    
    # Check Circlo API health
    logger.info("\n🔍 Checking Circlo API connection...")
    health = await client.health_check()
    
    if not health.get("success"):
        logger.error("❌ Circlo API is not accessible!")
        logger.error(f"   Error: {health.get('error')}")
        return
    
    logger.info("✅ Circlo API is healthy")
    logger.info(f"   WhatsApp enabled: {health.get('whatsapp_enabled')}")
    logger.info(f"   Memory enabled: {health.get('memory_enabled')}")
    
    # Register agents
    logger.info(f"\n📝 Registering {len(AGENTS)} agents...")
    results = []
    
    for agent_config in AGENTS:
        result = await register_agent(client, agent_config)
        results.append(result)
        await asyncio.sleep(1)  # Rate limiting
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Setup Summary")
    logger.info("=" * 60)
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    logger.info(f"✅ Successfully registered: {len(successful)}/{len(AGENTS)}")
    
    if successful:
        logger.info("\n✅ Registered agents:")
        for r in successful:
            logger.info(f"   - {r['agent']}")
    
    if failed:
        logger.info(f"\n⚠️  Failed/Skipped: {len(failed)}")
        for r in failed:
            logger.info(f"   - {r['agent']}: {r.get('error')}")
    
    logger.info("\n" + "=" * 60)
    logger.info("⚠️  IMPORTANT: Update agent endpoints in Circlo dashboard!")
    logger.info("Replace 'your-domain.com' with your actual deployment URL")
    logger.info("=" * 60)


async def test_circlo_integration():
    """Test Circlo integration"""
    logger.info("\n🧪 Testing Circlo Integration...")
    
    client = GetCircloClient()
    
    # Test 1: Health Check
    logger.info("\n1️⃣ Testing health check...")
    health = await client.health_check()
    logger.info(f"   Status: {health.get('status')}")
    
    # Test 2: Get User Preferences
    logger.info("\n2️⃣ Testing user preferences API...")
    prefs = await client.get_all_user_preferences(page=1, limit=5)
    if prefs.get("success"):
        logger.info(f"   Found {len(prefs.get('preferences', []))} user preferences")
    else:
        logger.info(f"   Error: {prefs.get('error')}")
    
    logger.info("\n✅ Integration tests completed!")


if __name__ == "__main__":
    import sys
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║         TrendScout Circlo Agents Setup Script            ║
╚═══════════════════════════════════════════════════════════╝

This script will:
1. Verify Circlo API connection
2. Register TrendScout agents on Circlo platform
3. Configure custom conversation endpoints

Make sure you have:
✓ GETCIRCLO_API_KEY set in .env
✓ Circlo API access
✓ Deployment URL ready (for webhook endpoints)

""")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        asyncio.run(test_circlo_integration())
    else:
        confirm = input("Proceed with agent registration? (y/n): ")
        
        if confirm.lower() == 'y':
            asyncio.run(setup_all_agents())
        else:
            print("Setup cancelled.")
