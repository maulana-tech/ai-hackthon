import logging
from typing import Dict, Any, List
from datetime import datetime
from openai import AsyncOpenAI

from app.config import get_settings
from app.agents.super_agent import SuperAgent
from app.integrations.getcirclo_client import GetCircloClient

logger = logging.getLogger(__name__)
settings = get_settings()

openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

class CircloConversationHandler:
    """
    Handle conversations from Circlo custom agent endpoints
    
    This agent processes incoming conversation requests from Circlo
    and routes them to appropriate TrendScout agents.
    """
    
    def __init__(self):
        self.name = "Circlo Conversation Handler"
        self.super_agent = SuperAgent()
        self.getcirclo = GetCircloClient()
        
    async def handle_conversation(
        self,
        history: List[Dict[str, str]],
        message: str,
        user: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Handle incoming conversation from Circlo
        
        Args:
            history: Conversation history [{"role": "user/assistant", "content": "..."}]
            message: Latest user message
            user: User info with preferences
            profile: Agent profile info
            
        Returns:
            {"response": "AI reply message"}
        """
        try:
            logger.info(f"Handling Circlo conversation from user {user.get('id')}")
            
            # Extract user context
            user_id = user.get("id")
            user_name = user.get("name")
            preferred_keywords = user.get("preferredKeywords", [])
            preferred_niches = user.get("preferredNiches", [])
            
            # Determine intent
            intent = await self._classify_intent(message, history)
            
            logger.info(f"Classified intent: {intent}")
            
            # Route to appropriate handler
            if intent == "trend_analysis":
                response = await self._handle_trend_query(
                    message, user_id, preferred_keywords, preferred_niches
                )
            elif intent == "supplier_search":
                response = await self._handle_supplier_query(
                    message, user_id
                )
            elif intent == "marketing_campaign":
                response = await self._handle_marketing_query(
                    message, user_id
                )
            elif intent == "greeting":
                response = await self._handle_greeting(user_name, user_id)
            elif intent == "help":
                response = await self._handle_help()
            else:
                response = await self._handle_general_query(
                    message, history, user_id
                )
            
            # Log interaction
            await self.getcirclo.save_interaction_history(
                user_id=user_id,
                interaction={
                    "message": message,
                    "response": response,
                    "intent": intent,
                    "agent": profile.get("name")
                }
            )
            
            return {"response": response}
            
        except Exception as e:
            logger.error(f"Error handling Circlo conversation: {str(e)}")
            return {
                "response": "Maaf, terjadi kesalahan. Silakan coba lagi atau hubungi admin."
            }
    
    async def _classify_intent(
        self,
        message: str,
        history: List[Dict[str, str]]
    ) -> str:
        """Classify user intent using LLM"""
        try:
            system_prompt = """You are an intent classifier for TrendScout AI.
            
Classify the user's message into one of these categories:
- trend_analysis: User asking about trending products, market trends
- supplier_search: User looking for suppliers, vendors, manufacturers
- marketing_campaign: User wants to create marketing content or campaigns
- greeting: User greeting or introducing themselves
- help: User asking for help or instructions
- general: Anything else

Respond with only the category name."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Message: {message}"}
            ]
            
            response = await openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3,
                max_tokens=50
            )
            
            intent = response.choices[0].message.content.strip().lower()
            
            return intent if intent in [
                "trend_analysis", "supplier_search", "marketing_campaign",
                "greeting", "help", "general"
            ] else "general"
            
        except Exception as e:
            logger.error(f"Intent classification error: {str(e)}")
            return "general"
    
    async def _handle_trend_query(
        self,
        message: str,
        user_id: str,
        preferred_keywords: List[str],
        preferred_niches: List[str]
    ) -> str:
        """Handle trend analysis queries"""
        
        # Extract product category from message
        category = await self._extract_product_category(message)
        
        response = f"""🔍 Saya akan mencari tren produk {category} untuk Anda!

Mohon tunggu sebentar, saya sedang:
1. Menganalisis tren global dari Google Trends, TikTok, dan Amazon
2. Mencari supplier terpercaya di Indonesia
3. Mempersiapkan laporan lengkap

Estimasi waktu: 30-60 detik.

Anda akan mendapatkan:
✅ 3 produk trending teratas
✅ 5 supplier terpercaya dengan kontak langsung
✅ Rekomendasi harga dan MOQ
✅ Link untuk mulai marketing campaign

Saya akan mulai proses analisis sekarang..."""

        # Trigger async super agent processing
        import asyncio
        asyncio.create_task(
            self.super_agent.process_query(
                query=message,
                user_id=user_id
            )
        )
        
        return response
    
    async def _handle_supplier_query(
        self,
        message: str,
        user_id: str
    ) -> str:
        """Handle supplier search queries"""
        
        product = await self._extract_product_category(message)
        
        return f"""🔎 Mencari supplier {product} di Indonesia...

Saya akan scan:
- Tokopedia & Shopee (top rated sellers)
- Supplier marketplace B2B
- Grup WhatsApp supplier terpercaya

Filter yang digunakan:
✅ Rating > 4.5/5
✅ Lokasi Indonesia
✅ Stok tersedia
✅ Melayani grosir/reseller

Hasil akan segera saya kirimkan!"""
    
    async def _handle_marketing_query(
        self,
        message: str,
        user_id: str
    ) -> str:
        """Handle marketing campaign queries"""
        
        return """🎨 Marketing Campaign Generator siap!

Saya bisa bantu Anda:

1. **Content Creation**
   - Generate post Instagram/TikTok
   - Buat caption menarik + hashtags
   - Design visual dengan Canva

2. **Campaign Planning**
   - Target audience analysis
   - Budget optimization
   - Best posting times

3. **Auto Engagement**
   - Auto-reply comments
   - DM automation
   - Lead tracking

Produk apa yang ingin Anda promosikan?"""
    
    async def _handle_greeting(self, user_name: str, user_id: str) -> str:
        """Handle greeting messages"""
        
        # Get user history to personalize
        history = await self.getcirclo.get_interaction_history(user_id, limit=1)
        
        if history:
            return f"""Hai lagi {user_name}! 👋

Senang bertemu lagi! Saya siap bantu Anda:

💡 Cari produk trending
🏭 Hubungkan dengan supplier Indonesia
📱 Launch marketing campaign

Mau cari produk apa hari ini?"""
        else:
            return f"""Hai {user_name}! 👋 Saya TrendScout AI!

Saya adalah Super AI-Agent yang bisa:

🔍 **Analisis Tren Global**
- Real-time trending products dari Google, TikTok, Amazon
- Market insights & growth predictions

🏭 **Connect Supplier Indonesia**  
- Auto-find 5 supplier terpercaya
- Direct contact via WhatsApp/Email
- Compare harga & MOQ

📱 **Auto Marketing Campaign**
- Generate konten Instagram/TikTok
- Setup ads & boosting
- Auto-engagement bot

Mau mulai dari mana? Coba tanya:
"Cari produk home decor yang lagi tren"
"Supplier skincare terpercaya di Jakarta"
"Buatkan campaign untuk LED Face Mask"""
    
    async def _handle_help(self) -> str:
        """Handle help requests"""
        
        return """❓ TrendScout AI - Panduan Penggunaan

**Commands yang bisa Anda coba:**

1️⃣ **Analisis Tren**
   "Cari produk [kategori] yang lagi tren"
   "Trend apa yang naik di [negara]?"

2️⃣ **Cari Supplier**
   "Supplier [produk] di [kota]"
   "Kontak supplier terpercaya untuk [produk]"

3️⃣ **Marketing Campaign**
   "Buatkan campaign Instagram untuk [produk]"
   "Generate konten TikTok [produk]"

4️⃣ **Status & History**
   "Status job saya"
   "History pencarian saya"

💡 **Tips:**
- Semakin spesifik query Anda, semakin akurat hasilnya
- Simpan preferensi untuk rekomendasi lebih personal
- Aktifkan notifikasi untuk update supplier response

Mau coba sekarang?"""
    
    async def _handle_general_query(
        self,
        message: str,
        history: List[Dict[str, str]],
        user_id: str
    ) -> str:
        """Handle general queries using GPT"""
        try:
            system_prompt = """You are TrendScout AI, a helpful assistant for finding trending products and connecting with Indonesian suppliers.

You can help users:
- Find trending products globally
- Connect with suppliers in Indonesia
- Create marketing campaigns

Be friendly, concise, and always guide users to use your main features.
Respond in Indonesian (Bahasa Indonesia)."""

            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history
            for msg in history[-5:]:  # Last 5 messages
                messages.append(msg)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            response = await openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"General query error: {str(e)}")
            return "Maaf, saya tidak mengerti. Bisa tolong diulangi atau coba tanya tentang tren produk?"
    
    async def _extract_product_category(self, message: str) -> str:
        """Extract product category from message"""
        try:
            response = await openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract the product category from the user's message. Respond with only the category name in 1-3 words."},
                    {"role": "user", "content": message}
                ],
                temperature=0.3,
                max_tokens=20
            )
            
            category = response.choices[0].message.content.strip()
            return category
            
        except:
            return "general products"
