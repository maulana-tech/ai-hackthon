#!/usr/bin/env python3
"""Test Qwen Coder configuration"""

from app.config import get_settings

settings = get_settings()

print("\n" + "="*70)
print("Current LLM Configuration")
print("="*70 + "\n")

print(f"Provider: {settings.llm_provider}")
print(f"Model: {settings.llm_model}")
print(f"OpenRouter Key: {'✅ Set' if settings.openrouter_api_key else '❌ Not set'}")
print(f"OpenAI Key: {'✅ Set' if settings.openai_api_key else '❌ Not set'}")

print("\n" + "="*70)

if settings.llm_provider == "openrouter" and settings.openrouter_api_key:
    print("✅ Ready to use Qwen Coder via OpenRouter!")
    print("\nNext: Run intent classifier test:")
    print("   uv run python test_intent_only.py")
elif settings.openai_api_key:
    print("⚠️  Using OpenAI fallback")
    print("\nTo use Qwen Coder, add to .env:")
    print("   OPENROUTER_API_KEY=sk-or-v1-your-key")
    print("   LLM_PROVIDER=openrouter")
    print("   LLM_MODEL=qwen/qwen-2.5-coder-32b-instruct")
else:
    print("❌ No LLM API key configured")
    print("\nAdd to .env:")
    print("   OPENROUTER_API_KEY=sk-or-v1-your-key")
    print("   LLM_PROVIDER=openrouter")
    print("   LLM_MODEL=qwen/qwen-2.5-coder-32b-instruct")

print("="*70 + "\n")
