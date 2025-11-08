# OpenRouter Setup Guide

## Why OpenRouter?

OpenRouter provides access to multiple LLM models (including Qwen, Claude, Llama, GPT-4) through a single API:

✅ **Cheaper** - Qwen 2.5 72B is ~10x cheaper than GPT-3.5
✅ **Faster** - Multiple model options
✅ **Reliable** - Fallback to other models if one is down
✅ **No Quota Issues** - Pay-as-you-go pricing

## Pricing Comparison

| Model | Provider | Price (per 1M tokens) |
|-------|----------|----------------------|
| GPT-3.5 Turbo | OpenAI | $0.50 - $1.50 |
| **Qwen 2.5 Coder 32B** | **OpenRouter** | **$0.05 - $0.12** ⭐ |
| Qwen 2.5 72B | OpenRouter | $0.09 - $0.18 |
| Llama 3.1 70B | OpenRouter | $0.18 - $0.36 |
| Claude 3.5 Sonnet | OpenRouter | $3.00 - $15.00 |

## Setup Steps

### 1. Get OpenRouter API Key

1. Go to https://openrouter.ai/
2. Sign up / Log in
3. Go to https://openrouter.ai/keys
4. Create new API key
5. Copy the key (starts with `sk-or-v1-...`)

### 2. Add to .env

```bash
# Copy .env.example to .env
cp .env.example .env

# Then edit .env and add your actual OpenRouter key:
OPENROUTER_API_KEY=sk-or-v1-YOUR-ACTUAL-KEY-HERE
LLM_PROVIDER=openrouter
LLM_MODEL=qwen/qwen-2.5-coder-32b-instruct
```

### 3. Test Configuration

```bash
# Test intent classifier with OpenRouter
uv run python test_intent_only.py
```

## Available Models

### Budget Models (Recommended for Intent Classification)

```bash
# Qwen 2.5 Coder 32B - BEST FOR STRUCTURED TASKS ⭐
LLM_MODEL=qwen/qwen-2.5-coder-32b-instruct
# Why: Optimized for JSON output, structured data, fastest response
# Price: ~$0.05-0.12 per 1M tokens

# Qwen 2.5 72B - General Purpose
LLM_MODEL=qwen/qwen-2.5-72b-instruct
# Why: Larger context, better reasoning
# Price: ~$0.09-0.18 per 1M tokens

# Llama 3.1 70B - Good Alternative
LLM_MODEL=meta-llama/llama-3.1-70b-instruct

# Gemini Flash - Fast & Cheap
LLM_MODEL=google/gemini-flash-1.5
```

### Premium Models (For Complex Tasks)

```bash
# Claude 3.5 Sonnet - Best Quality
LLM_MODEL=anthropic/claude-3.5-sonnet

# GPT-4 Turbo
LLM_MODEL=openai/gpt-4-turbo

# Gemini Pro 1.5
LLM_MODEL=google/gemini-pro-1.5
```

## Configuration Options

### Option 1: OpenRouter (Recommended)

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key
LLM_PROVIDER=openrouter
LLM_MODEL=qwen/qwen-2.5-coder-32b-instruct
OPENAI_API_KEY=  # Leave empty
```

### Option 2: OpenAI (Fallback)

```bash
OPENROUTER_API_KEY=  # Leave empty
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key
```

### Option 3: Auto-Fallback

```bash
# Try OpenRouter first, fallback to OpenAI, then fallback to keyword-based
OPENROUTER_API_KEY=sk-or-v1-your-key
LLM_PROVIDER=openrouter
LLM_MODEL=qwen/qwen-2.5-coder-32b-instruct
OPENAI_API_KEY=sk-your-openai-key  # Fallback
```

## What Changed?

### Files Modified:

1. **app/config.py**
   - Added `openrouter_api_key` field
   - Added `llm_provider` field (openai/openrouter)
   - Added `llm_model` field (model selection)

2. **app/agents/intent_classifier.py**
   - Dynamic LLM client initialization
   - OpenRouter support with base_url
   - Better JSON extraction for non-OpenAI models
   - Fallback to keyword-based classification

3. **app/agents/circlo_conversation_handler.py**
   - Updated to use dynamic LLM client
   - Support for OpenRouter models

4. **.env.example**
   - Added OpenRouter configuration
   - Updated comments with pricing info

5. **.env.openrouter** (NEW)
   - Template for OpenRouter setup
   - Multiple model examples

## Usage in Code

The changes are transparent - no code changes needed:

```python
# Intent Classifier automatically uses configured LLM
from app.agents.intent_classifier import IntentClassifier

classifier = IntentClassifier()
result = await classifier.classify("Cari supplier tas macrame")

# Result structure same regardless of provider
{
  "intent": "find_suppliers",
  "confidence": 0.9,
  "parameters": {
    "product_name": "tas macrame"
  }
}
```

## Testing Different Models

```bash
# Test with Qwen 2.5 Coder 32B (Recommended)
export LLM_MODEL=qwen/qwen-2.5-coder-32b-instruct
uv run python test_intent_only.py

# Test with Qwen 2.5 72B (Larger model)
export LLM_MODEL=qwen/qwen-2.5-72b-instruct
uv run python test_intent_only.py

# Test with Claude 3.5 Sonnet (Premium)
export LLM_MODEL=anthropic/claude-3.5-sonnet
uv run python test_intent_only.py

# Test with Llama 3.1 70B (Alternative)
export LLM_MODEL=meta-llama/llama-3.1-70b-instruct
uv run python test_intent_only.py
```

## Monitoring Usage

1. Go to https://openrouter.ai/activity
2. View API calls and costs
3. Set spending limits if needed

## Troubleshooting

### Error: "No LLM API key configured"

**Solution:** Add OpenRouter key to .env:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key
```

### Error: "Model not found"

**Solution:** Check model name at https://openrouter.ai/models
```bash
# Correct format:
LLM_MODEL=qwen/qwen-2.5-coder-32b-instruct

# Not:
LLM_MODEL=qwen-coder
LLM_MODEL=qwen3-coder
```

### Fallback to Keyword Classification

This is normal if:
- No API key configured
- API quota exceeded
- Network error

The system will still work using keyword-based classification.

## Cost Estimation

For TrendScout typical usage:

- **Intent Classification**: ~100 tokens per request
- **1000 requests**: ~100K tokens
- **Cost with Qwen 2.5**: $0.01 - $0.02
- **Cost with GPT-3.5**: $0.05 - $0.15

**Savings: ~80-90% cheaper with OpenRouter!**

## Next Steps

1. ✅ Get OpenRouter API key
2. ✅ Update .env file
3. ✅ Test with `test_intent_only.py`
4. ✅ Run full agent tests
5. ✅ Monitor usage at openrouter.ai/activity

## Links

- OpenRouter Website: https://openrouter.ai/
- Model List: https://openrouter.ai/models
- API Docs: https://openrouter.ai/docs
- Pricing: https://openrouter.ai/docs/pricing
