# TrendScout Tests

This folder contains test scripts for validation and debugging.

## 🧪 Test Scripts

### Configuration Tests

**test_qwen_config.py** - Verify LLM configuration
- Check OpenRouter API key
- Verify LLM provider settings
- Show current configuration
```bash
uv run python tests/test_qwen_config.py
```

**test_openrouter_quick.py** - OpenRouter client test
- Verify OpenRouter client initialization
- Check base_url support
- Quick connectivity test
```bash
uv run python tests/test_openrouter_quick.py
```

### Component Tests

**test_intent_only.py** - Intent classifier test
- Test 6 different intents
- Verify parameter extraction
- Check Indonesian language support
```bash
uv run python tests/test_intent_only.py
```

**test_apify.py** - Apify integration test
- Test Apify client
- Verify marketplace scrapers
- Check actor runs
```bash
uv run python tests/test_apify.py
```

**test_indonetwork.py** - Indonetwork scraper test
- Test B2B marketplace scraping
- Verify data extraction
- Check product parsing
```bash
uv run python tests/test_indonetwork.py
```

**test_agent.py** - Agent functionality test
- Test individual agents
- Verify workflows
- Check integrations
```bash
uv run python tests/test_agent.py
```

### End-to-End Tests

**test_super_agent_flow.py** - Full workflow test
- Test complete agent pipeline
- Verify all 5 workflows
- End-to-end validation
```bash
uv run python tests/test_super_agent_flow.py
```

**run_real_scraping.py** - Real scraping test
- Test with real websites
- Verify data quality
- Performance testing
```bash
uv run python tests/run_real_scraping.py
```

## 🎯 Test Sequence (Recommended)

### 1. Initial Setup
```bash
# Test configuration first
uv run python tests/test_qwen_config.py
uv run python tests/test_openrouter_quick.py
```

### 2. Component Testing
```bash
# Test each component
uv run python tests/test_intent_only.py
uv run python tests/test_apify.py
uv run python tests/test_agent.py
```

### 3. Integration Testing
```bash
# Test full workflows
uv run python tests/test_super_agent_flow.py
uv run python tests/run_real_scraping.py
```

## 📊 Expected Results

### test_qwen_config.py
```
✅ Provider: openrouter
✅ Model: qwen/qwen-2.5-coder-32b-instruct
✅ OpenRouter Key: Set
```

### test_intent_only.py
```
✅ Intent: find_suppliers
✅ Confidence: 0.92
✅ Parameters: {"product_name": "tas macrame"}
```

### test_super_agent_flow.py
```
✅ Intent classification: PASS
✅ Supplier search: PASS
✅ Full pipeline: PASS
```

## 🐛 Troubleshooting

### "No LLM API key configured"
→ Add `OPENROUTER_API_KEY` to `.env`

### "Firecrawl API error"
→ Check `FIRECRAWL_API_KEY` is valid

### "Module not found"
→ Run `uv pip install -r requirements.txt`

### Tests timeout
→ Scraping tests can take 1-3 minutes, this is normal

## 💡 Tips

- Run configuration tests first
- Use component tests for debugging
- Run full tests before deployment
- Check logs in `../logs/` for details

## 📁 Related Folders

- `/app` - Application code being tested
- `/scripts` - Operational scripts
- `/docs` - Test documentation
- `/logs` - Test output logs

Back to [Main README](../README.md)
