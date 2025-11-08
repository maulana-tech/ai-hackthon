import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure LLM client based on provider
if settings.llm_provider == "openrouter" and settings.openrouter_api_key:
    logger.info(f"Using OpenRouter with model: {settings.llm_model}")
    llm_client = AsyncOpenAI(
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    llm_model = settings.llm_model
elif settings.openai_api_key:
    logger.info("Using OpenAI")
    llm_client = AsyncOpenAI(api_key=settings.openai_api_key)
    llm_model = "gpt-3.5-turbo"
else:
    logger.warning("No LLM API key configured, will use fallback classification")
    llm_client = None
    llm_model = None


class IntentClassifier:
    """
    Classify user intent and extract parameters from natural language queries
    
    Intents:
    - find_trending_products: User wants to know what's trending
    - find_suppliers: User wants to find suppliers for a product
    - find_trending_suppliers: User wants both (trending + suppliers)
    - contact_suppliers: User wants to contact suppliers
    - create_campaign: User wants marketing campaign
    - get_status: User checking job status
    - help: User needs help
    """
    
    def __init__(self):
        self.name = "Intent Classifier"
        
    async def classify(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Classify user intent and extract parameters
        
        Args:
            query: User's natural language query
            context: Optional user context (history, preferences)
            
        Returns:
            {
                "intent": "find_trending_suppliers",
                "confidence": 0.95,
                "parameters": {
                    "product_category": "skincare",
                    "location": "Jakarta",
                    "min_rating": 4.0,
                    "limit": 5
                }
            }
        """
        try:
            # Check if LLM client is available
            if not llm_client:
                logger.warning("No LLM client available, using fallback")
                return self._fallback_classify(query)
            
            logger.info(f"Classifying intent for query: {query}")
            
            system_prompt = self._get_system_prompt()
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            # Add context if available
            if context and context.get("history"):
                context_msg = f"User's recent queries: {context['history'][-3:]}"
                messages.insert(1, {"role": "system", "content": context_msg})
            
            # Use configured LLM model
            response = await llm_client.chat.completions.create(
                model=llm_model,
                messages=messages,
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"} if settings.llm_provider == "openai" else None
            )
            
            import json
            content = response.choices[0].message.content
            
            # Try to extract JSON from response
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # If model returns markdown code block, extract JSON
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                else:
                    # Try to find any JSON object in the response
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group(0))
                    else:
                        raise ValueError("Could not extract JSON from response")
            
            logger.info(f"Classified intent: {result.get('intent')} (confidence: {result.get('confidence')})")
            
            return result
            
        except Exception as e:
            logger.error(f"Intent classification error: {str(e)}")
            # Fallback to basic classification
            return self._fallback_classify(query)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for intent classification"""
        return """You are an intent classifier for TrendScout, a supplier discovery platform.

Analyze the user's query and return a JSON object with:
1. "intent" - the primary intent (choose from list below)
2. "confidence" - confidence score (0-1)
3. "parameters" - extracted parameters

Available intents:
- "find_bestsellers": User wants to find the most popular/bestselling products from marketplaces (based on sales data)
- "find_trending_products": User wants to know what products are trending
- "find_suppliers": User wants to find suppliers for a specific product
- "find_trending_suppliers": User wants both trending analysis AND suppliers (most common)
- "contact_suppliers": User wants to contact/message suppliers
- "create_campaign": User wants to create marketing campaign
- "get_status": User checking status of previous request
- "help": User needs help or instructions

Extract these parameters if mentioned:
- "product_category": product type/category (e.g., "skincare", "fashion", "electronics")
- "product_name": specific product name (e.g., "LED face mask", "macrame bag")
- "location": preferred supplier location (e.g., "Jakarta", "Surabaya", "Indonesia")
- "min_rating": minimum supplier rating (default: 4.0)
- "limit": number of results wanted (default: 5)
- "budget_min": minimum budget
- "budget_max": maximum budget
- "contact_method": preferred contact (e.g., "whatsapp", "email")

Examples:

Query: "Carikan produk yang paling laris"
Output: {
  "intent": "find_bestsellers",
  "confidence": 0.95,
  "parameters": {
    "limit": 10,
    "min_sold": 100
  }
}

Query: "Produk fashion apa yang paling banyak terjual di Tokopedia?"
Output: {
  "intent": "find_bestsellers",
  "confidence": 0.9,
  "parameters": {
    "product_category": "fashion",
    "marketplace": "tokopedia"
  }
}

Query: "Cari produk skincare yang lagi tren"
Output: {
  "intent": "find_trending_products",
  "confidence": 0.95,
  "parameters": {
    "product_category": "skincare"
  }
}

Query: "Cari supplier tas macrame di Jakarta"
Output: {
  "intent": "find_suppliers",
  "confidence": 0.9,
  "parameters": {
    "product_name": "tas macrame",
    "location": "Jakarta"
  }
}

Query: "Cari produk trending home decor dan supplier nya di Bali"
Output: {
  "intent": "find_trending_suppliers",
  "confidence": 0.95,
  "parameters": {
    "product_category": "home decor",
    "location": "Bali"
  }
}

Query: "Hubungi supplier yang tadi"
Output: {
  "intent": "contact_suppliers",
  "confidence": 0.85,
  "parameters": {}
}

Always respond with valid JSON only, no additional text."""
    
    def _fallback_classify(self, query: str) -> Dict[str, Any]:
        """Simple fallback classification using keywords"""
        query_lower = query.lower()
        
        # Check for bestseller/terlaris keywords first (highest priority)
        if any(word in query_lower for word in ["terlaris", "paling laris", "bestseller", "best seller", "paling banyak terjual", "most sold"]):
            return {
                "intent": "find_bestsellers",
                "confidence": 0.8,
                "parameters": {
                    "limit": 10,
                    "min_sold": 100
                }
            }
        
        # Keyword-based classification
        if any(word in query_lower for word in ["trending", "tren", "viral", "populer"]):
            if any(word in query_lower for word in ["supplier", "penjual", "toko", "hubungi"]):
                return {
                    "intent": "find_trending_suppliers",
                    "confidence": 0.7,
                    "parameters": {}
                }
            return {
                "intent": "find_trending_products",
                "confidence": 0.7,
                "parameters": {}
            }
        
        if any(word in query_lower for word in ["supplier", "penjual", "toko", "cari"]):
            return {
                "intent": "find_suppliers",
                "confidence": 0.7,
                "parameters": {}
            }
        
        if any(word in query_lower for word in ["hubungi", "contact", "kirim pesan", "whatsapp"]):
            return {
                "intent": "contact_suppliers",
                "confidence": 0.7,
                "parameters": {}
            }
        
        if any(word in query_lower for word in ["campaign", "kampanye", "promosi", "iklan"]):
            return {
                "intent": "create_campaign",
                "confidence": 0.7,
                "parameters": {}
            }
        
        if any(word in query_lower for word in ["status", "hasil", "progress"]):
            return {
                "intent": "get_status",
                "confidence": 0.7,
                "parameters": {}
            }
        
        # Default to find_trending_suppliers
        return {
            "intent": "find_trending_suppliers",
            "confidence": 0.5,
            "parameters": {}
        }
