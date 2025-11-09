"""
LLM Client - Interface for AI model generation

Supports:
- Google Gemini (Primary - Fast)
- OpenRouter (Qwen 3 models - Fallback)
- OpenAI (GPT models)
- Simple fallback responses
"""
import logging
import httpx
from typing import Optional, Dict, Any
import json

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMClient:
    """
    Client for LLM API calls with specialized provider routing
    
    Strategy:
    - Gemini: Fast content generation (taglines, messaging, schedules)
    - Qwen 3: Complex reasoning (budget calculations, allocations)
    """
    
    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        
        # Set API keys
        self.gemini_key = settings.gemini_api_key
        self.openrouter_key = settings.openrouter_api_key
        self.openai_key = settings.openai_api_key
        
        # Set default API key based on provider
        if self.provider == "gemini":
            self.api_key = self.gemini_key
        elif self.provider == "openrouter":
            self.api_key = self.openrouter_key
        else:
            self.api_key = self.openai_key
        
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate text using LLM with dual fallback
        
        Flow:
        1. Try Gemini (fast, free tier)
        2. Fallback to OpenRouter Qwen 3
        3. Fallback to simple template
        
        Args:
            prompt: Input prompt
            temperature: Creativity (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Generated text
        """
        try:
            # Primary: Try Gemini (fast and free)
            if self.provider == "gemini":
                result = await self._generate_gemini(prompt, temperature, max_tokens)
                if result:
                    return result
                
                # Fallback to OpenRouter Qwen 3
                logger.info("Gemini failed, falling back to OpenRouter Qwen 3")
                return await self._generate_openrouter(prompt, temperature, max_tokens)
            
            # OpenRouter Qwen 3
            elif self.provider == "openrouter":
                return await self._generate_openrouter(prompt, temperature, max_tokens)
            
            # OpenAI
            elif self.provider == "openai":
                return await self._generate_openai(prompt, temperature, max_tokens)
            
            else:
                return self._fallback_generate(prompt)
                
        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            return self._fallback_generate(prompt)
    
    async def _generate_gemini(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Optional[str]:
        """
        Generate using Google Gemini API (Fast & Free)
        
        Uses gemini-1.5-flash for speed
        """
        try:
            # Gemini uses v1 endpoint (v1beta deprecated for some models)
            # Use gemini-1.5-flash-latest for stable API
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={self.api_key}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [{
                                "text": prompt
                            }]
                        }],
                        "generationConfig": {
                            "temperature": temperature,
                            "maxOutputTokens": max_tokens,
                            "topP": 0.95,
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract text from Gemini response format
                    if "candidates" in data and len(data["candidates"]) > 0:
                        candidate = data["candidates"][0]
                        if "content" in candidate:
                            parts = candidate["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                result = parts[0]["text"]
                                logger.info(f"✅ Gemini generated {len(result)} chars")
                                return result
                    
                    logger.warning("Gemini response format unexpected")
                    return None
                else:
                    logger.error(f"Gemini API error: {response.status_code} - {response.text[:200]}")
                    return None
                    
        except Exception as e:
            logger.error(f"Gemini generation error: {str(e)}")
            return None
    
    async def _generate_openrouter(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using OpenRouter API (Qwen 3)"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",  # Use explicit key
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://trendscout.ai",  # Required by OpenRouter
                        "X-Title": "TrendScout AI Agent"  # Optional but recommended
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = data["choices"][0]["message"]["content"]
                    logger.info(f"✅ OpenRouter generated {len(result)} chars")
                    return result
                else:
                    error_text = response.text[:500]
                    logger.error(f"OpenRouter API error: {response.status_code} - {error_text}")
                    return self._fallback_generate(prompt)
                    
        except Exception as e:
            logger.error(f"OpenRouter error: {str(e)}")
            return self._fallback_generate(prompt)
    
    async def _generate_openai(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using OpenAI API"""
        try:
            # Similar to OpenRouter but with OpenAI endpoint
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"OpenAI API error: {response.status_code}")
                    return self._fallback_generate(prompt)
                    
        except Exception as e:
            logger.error(f"OpenAI error: {str(e)}")
            return self._fallback_generate(prompt)
    
    async def generate_budget(
        self,
        prompt: str,
        temperature: float = 0.5,
        max_tokens: int = 1500
    ) -> str:
        """
        Generate budget allocation using Qwen 3 (specialized for calculations)
        
        Qwen 3 has better reasoning for:
        - Budget calculations
        - Percentage allocations
        - ROI estimations
        - Complex math
        
        Args:
            prompt: Budget-related prompt
            temperature: Lower for more consistent calculations
            max_tokens: Budget needs detailed breakdowns
            
        Returns:
            Budget allocation in JSON format
        """
        logger.info("🧮 Using Qwen 3 for budget calculation...")
        
        try:
            # Force use of OpenRouter Qwen 3 for budget
            result = await self._generate_openrouter(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract JSON if wrapped in <think> tags
            if "<think>" in result:
                # Qwen 3 sometimes wraps reasoning in think tags
                # Extract the actual JSON response
                import re
                json_match = re.search(r'\{[\s\S]*\}', result)
                if json_match:
                    return json_match.group(0)
            
            return result
            
        except Exception as e:
            logger.error(f"Qwen 3 budget generation failed: {str(e)}")
            return self._fallback_budget_generate(prompt)
    
    def _fallback_budget_generate(self, prompt: str) -> str:
        """Fallback budget allocation template"""
        return '''
{
  "total_budget": "Rp 5.000.000",
  "allocation": {
    "social_media_ads": {
      "percentage": "40%",
      "amount": "Rp 2.000.000",
      "platforms": ["Instagram", "Facebook", "TikTok"]
    },
    "influencer_marketing": {
      "percentage": "25%",
      "amount": "Rp 1.250.000"
    },
    "content_creation": {
      "percentage": "20%",
      "amount": "Rp 1.000.000"
    },
    "email_marketing": {
      "percentage": "10%",
      "amount": "Rp 500.000"
    },
    "retargeting": {
      "percentage": "5%",
      "amount": "Rp 250.000"
    }
  },
  "daily_budget": "Rp 166.667",
  "recommendations": [
    "Start with smaller budgets and scale based on performance",
    "Focus 60% budget on best performing platform",
    "Reserve 10% for testing new channels"
  ]
}
'''.strip()
    
    def _fallback_generate(self, prompt: str) -> str:
        """Fallback simple response when API unavailable"""
        logger.warning("Using fallback generation (no LLM API)")
        
        # Simple template-based responses
        if "campaign" in prompt.lower():
            return '{"tagline": "Produk Berkualitas Harga Terjangkau!", "messaging": ["Kualitas terjamin", "Harga kompetitif"], "cta": "Beli Sekarang!"}'
        elif "budget" in prompt.lower():
            return '{"total_budget": "Rp 5.000.000", "allocation": {"social_media": "40%", "influencer": "30%"}}'
        elif "schedule" in prompt.lower():
            return '{"duration_days": 30, "phases": [{"phase": "Awareness", "week": "1-2"}]}'
        else:
            return "Campaign strategy generated successfully."


# Global instance
llm_client = LLMClient()
