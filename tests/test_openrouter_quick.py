#!/usr/bin/env python3
"""Quick test for OpenRouter configuration"""

import asyncio
from openai import AsyncOpenAI

async def test_openrouter():
    print("\n" + "="*70)
    print("OpenRouter Configuration Test")
    print("="*70 + "\n")
    
    # Test with a dummy key format
    print("ℹ️  Checking if OpenRouter client can be initialized...")
    
    try:
        # This will check if openai package supports the base_url parameter
        client = AsyncOpenAI(
            api_key="sk-or-v1-test-key",
            base_url="https://openrouter.ai/api/v1"
        )
        print("✅ OpenRouter client initialization: OK")
        print("✅ Base URL parameter: Supported")
        print()
        print("📝 Next steps:")
        print("   1. Get API key from: https://openrouter.ai/keys")
        print("   2. Add to .env:")
        print("      OPENROUTER_API_KEY=sk-or-v1-your-actual-key")
        print("      LLM_PROVIDER=openrouter")
        print("      LLM_MODEL=qwen/qwen-2.5-72b-instruct")
        print("   3. Run: uv run python test_intent_only.py")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("   OpenAI package might need update")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(test_openrouter())
