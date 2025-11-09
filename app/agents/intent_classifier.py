import logging
from typing import Dict, Any, Optional
import json
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


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
            # Check if Gemini API key is available
            if not settings.gemini_api_key:
                logger.warning("No Gemini API key, using fallback")
                return self._fallback_classify(query)
            
            logger.info(f"Classifying intent for query: {query}")
            
            system_prompt = self._get_system_prompt()
            full_prompt = f"{system_prompt}\n\nQuery: {query}"
            
            # Use Gemini for fast classification
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.gemini_api_key}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [{
                                "text": full_prompt
                            }]
                        }],
                        "generationConfig": {
                            "temperature": 0.3,
                            "maxOutputTokens": 500,
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract text from Gemini response
                    if "candidates" in data and len(data["candidates"]) > 0:
                        candidate = data["candidates"][0]
                        if "content" in candidate:
                            parts = candidate["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                content = parts[0]["text"]
                                
                                # Parse JSON response
                                import re
                                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                                if json_match:
                                    result = json.loads(json_match.group(0))
                                    logger.info(f"✅ Classified: {result.get('intent')} (confidence: {result.get('confidence')})")
                                    return result
                
                # Fallback if parsing fails
                logger.warning("Gemini response parsing failed, using fallback")
                return self._fallback_classify(query)
            
        except Exception as e:
            logger.error(f"Intent classification error: {str(e)}")
            # Fallback to keyword-based classification
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
- "marketplace": specific marketplace (e.g., "tokopedia", "amazon", "lazada", "shopee")
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
    "marketplace": "tokopedia",
    "limit": 10
  }
}

Query: "Best sellers Amazon electronics"
Output: {
  "intent": "find_bestsellers",
  "confidence": 0.95,
  "parameters": {
    "product_category": "electronics",
    "marketplace": "amazon",
    "limit": 10
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

Query: "Carikan supplier untuk skincare"
Output: {
  "intent": "find_suppliers",
  "confidence": 0.9,
  "parameters": {
    "product_name": "skincare"
  }
}

Query: "Produk terlaris di Tokopedia"
Output: {
  "intent": "find_bestsellers",
  "confidence": 0.95,
  "parameters": {
    "marketplace": "tokopedia",
    "limit": 10
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
        
        # Extract marketplace from query
        marketplace = None
        if "tokopedia" in query_lower:
            marketplace = "tokopedia"
        elif "amazon" in query_lower:
            marketplace = "amazon"
        elif "lazada" in query_lower:
            marketplace = "lazada"
        elif "shopee" in query_lower:
            marketplace = "shopee"
        
        # Check for bestseller/terlaris keywords first (highest priority)
        if any(word in query_lower for word in ["terlaris", "paling laris", "bestseller", "best seller", "paling banyak terjual", "most sold"]):
            params = {
                "limit": 10,
                "min_sold": 100
            }
            if marketplace:
                params["marketplace"] = marketplace
            
            return {
                "intent": "find_bestsellers",
                "confidence": 0.8,
                "parameters": params
            }
        
        # "Carikan supplier untuk X" = user wants to find suppliers (not bestsellers)
        if any(pattern in query_lower for pattern in ["carikan supplier", "supplier untuk", "cari supplier", "supplier terbaik", "supplier bagus"]):
            # Extract product name after "untuk" or after "supplier"
            product_name = None
            if "untuk" in query_lower:
                parts = query_lower.split("untuk")
                if len(parts) > 1:
                    product_name = parts[1].strip()
            elif "supplier" in query_lower:
                parts = query_lower.split("supplier")
                if len(parts) > 1:
                    product_name = parts[1].strip()
            
            return {
                "intent": "find_suppliers",
                "confidence": 0.85,
                "parameters": {
                    "product_name": product_name,
                    "limit": 10
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
        
        # Generic product search
        if any(word in query_lower for word in ["produk", "barang", "jual", "beli"]):
            return {
                "intent": "find_bestsellers",
                "confidence": 0.6,
                "parameters": {}
            }
        
        if any(word in query_lower for word in ["hubungi", "contact", "kirim pesan", "whatsapp", "kirim email", "kirimkan email", "email ke supplier"]):
            return {
                "intent": "contact_suppliers",
                "confidence": 0.8,
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
