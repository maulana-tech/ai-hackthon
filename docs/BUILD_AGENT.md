# Building the TrendScout AI Agent - Implementation Plan

## 🎯 Goal
Build a proper AI Super Agent that orchestrates multiple sub-agents to:
1. Analyze trending products
2. Find suppliers in Indonesia
3. Contact suppliers automatically
4. Generate reports

## 📋 Current Status

### ✅ Already Working:
1. **Supplier Scout Agent** - Scraping Indonetwork (working!)
2. **Firecrawl Integration** - API calls successful
3. **Apify Integration** - Code ready (needs API key config)
4. **GetCirclo Integration** - WhatsApp, Memory, Posts
5. **Data Models** - Pydantic schemas defined
6. **Outreach Agent** - Email & WhatsApp messaging

### 🔨 Need to Build:
1. **Super Agent** - Main orchestrator (needs improvement)
2. **Trend Analyst Agent** - Google Trends, TikTok analysis (needs work)
3. **Agent Workflow** - Proper async orchestration
4. **Memory Integration** - User context & preferences
5. **Response Generation** - Structured reports

## 🏗️ Implementation Steps

### Phase 1: Fix & Enhance Existing Agents

#### 1.1 Improve Supplier Scout Parser ✅ (DONE)
- ✅ Extract product links from search
- ✅ Scrape individual product pages
- ✅ Parse supplier information
- ⚠️ Need better regex for company names/contacts

#### 1.2 Enhance Trend Analyst Agent
**Current Issues:**
- Using Google Trends API (slow, rate limited)
- No TikTok/Instagram integration yet
- Need better trending detection

**Improvements:**
```python
# Add real-time trending detection
- Scrape Google Trends with Firecrawl
- Get TikTok hashtag data via Apify
- Parse Instagram trending via Apify
- Combine signals for trend score
```

#### 1.3 Build Proper Super Agent
**Current Issues:**
- Basic orchestration
- No proper error handling
- Missing progress tracking

**New Architecture:**
```python
class SuperAgent:
    async def execute_workflow(query, user_id):
        # 1. Parse user query
        intent = await parse_intent(query)
        
        # 2. Get user context from Circlo Memory
        context = await get_user_context(user_id)
        
        # 3. Execute sub-agents in order
        if intent == "find_trending_suppliers":
            # Step 1: Find trends
            trends = await trend_analyst.analyze(query)
            
            # Step 2: Find suppliers
            suppliers = await supplier_scout.find(trends[0])
            
            # Step 3: Contact suppliers
            messages = await outreach.contact(suppliers)
            
            # Step 4: Save to memory
            await memory.save(user_id, results)
            
            # Step 5: Generate report
            report = await generate_report(trends, suppliers, messages)
            
            return report
```

### Phase 2: Build Core AI Agent

#### 2.1 Intent Classification
```python
# Use OpenAI to classify user intent
intents = [
    "find_trending_products",
    "find_suppliers",
    "contact_suppliers",
    "create_marketing_campaign",
    "get_status"
]

# Extract parameters from query
```

#### 2.2 Context Management
```python
# Get user preferences from Circlo
preferences = await circlo.get_user_preference(user_id)

# Store in agent context
context = {
    "user_id": user_id,
    "preferences": preferences,
    "history": await circlo.get_interaction_history(user_id),
    "current_query": query
}
```

#### 2.3 Agent Orchestration
```python
# Sequential execution with progress updates
async def orchestrate(steps):
    results = {}
    for step in steps:
        progress = await execute_step(step)
        results[step.name] = progress
        await notify_user(progress)
    return results
```

### Phase 3: Integrate Everything

#### 3.1 API Endpoints
```python
POST /api/agent/execute
{
    "query": "Cari produk trending dan supplier di Jakarta",
    "user_id": "user123"
}

Response:
{
    "job_id": "abc123",
    "status": "processing",
    "steps": [
        {"name": "trend_analysis", "status": "completed"},
        {"name": "supplier_search", "status": "in_progress"},
        {"name": "outreach", "status": "pending"}
    ]
}
```

#### 3.2 WebSocket for Real-time Updates
```python
# Push updates to client
ws.send({
    "job_id": "abc123",
    "step": "supplier_search",
    "progress": 60,
    "message": "Found 5 suppliers..."
})
```

#### 3.3 Circlo Integration
```python
# Handle Circlo webhook
POST /api/circlo/circlo-hook
→ Parse message
→ Execute Super Agent
→ Return response to Circlo
→ User sees reply in Circlo chat
```

## 🎯 Immediate Next Steps

### Step 1: Improve Supplier Scout ✅
- [x] Fix parser to extract better company names
- [x] Get real data (bulk scraping in progress)
- [ ] Add contact info extraction
- [ ] Add pagination support

### Step 2: Build Trend Analyst (NOW)
```python
# Quick implementation using Firecrawl
class TrendAnalystAgent:
    async def analyze_trends(product_category):
        # 1. Scrape Google Trends
        trends_data = await firecrawl.scrape(
            f"https://trends.google.com/trends/explore?q={product_category}"
        )
        
        # 2. Parse trending products
        trending = parse_trends(trends_data)
        
        # 3. Score and rank
        scored = score_trends(trending)
        
        return scored[:5]
```

### Step 3: Rebuild Super Agent (NEXT)
```python
# Full orchestration
class SuperAgent:
    def __init__(self):
        self.trend_analyst = TrendAnalystAgent()
        self.supplier_scout = SupplierScoutAgent()
        self.outreach = OutreachAgent()
        self.memory = MemoryKeeperAgent()
        self.circlo = GetCircloClient()
    
    async def execute(query, user_id):
        # Get context
        context = await self.get_context(user_id)
        
        # Parse intent
        intent = await self.classify_intent(query, context)
        
        # Execute workflow
        if intent == "find_trending_suppliers":
            return await self.workflow_trending_suppliers(query, context)
        elif intent == "find_suppliers_only":
            return await self.workflow_find_suppliers(query, context)
        ...
    
    async def workflow_trending_suppliers(query, context):
        # Full pipeline
        trends = await self.trend_analyst.analyze(query)
        suppliers = await self.supplier_scout.find(trends[0].name)
        messages = await self.outreach.contact(suppliers[:5])
        
        report = self.generate_report(trends, suppliers, messages)
        await self.memory.save(context.user_id, report)
        
        return report
```

### Step 4: Test End-to-End
```bash
# Test full workflow
python test_super_agent.py

# Expected flow:
User: "Cari produk skincare trending dan supplier di Jakarta"
→ Trend Analyst: Find trending skincare
→ Supplier Scout: Find Jakarta suppliers
→ Outreach: Send WhatsApp to top 5
→ Memory: Save results
→ Response: Complete report
```

## 📊 Success Metrics

1. **Scraping Success Rate**: >80% ✅ (Currently working)
2. **Data Quality**: >70% complete supplier info ⚠️ (Need improvement)
3. **Response Time**: <60s end-to-end ⚠️ (Need optimization)
4. **Agent Coordination**: Proper orchestration ❌ (Need to build)

## 🚀 Ready to Build!

Files to create/modify:
1. `app/agents/trend_analyst.py` - Enhance with real scraping
2. `app/agents/super_agent.py` - Rebuild with proper orchestration
3. `app/agents/intent_classifier.py` - NEW - Intent classification
4. `test_super_agent_flow.py` - NEW - End-to-end test

Let's start building the proper AI Agent now! 🎯
