"""
Document Generation Service - Create shareable campaign documents

Creates markdown/text documents that can be shared via:
1. GitHub Gist (public, permanent)
2. Pastebin-like services
3. Direct file download
"""
import logging
import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DocumentService:
    """
    Service for creating and sharing campaign documents
    
    Strategy: Use GitHub Gist API (no auth required for public gists)
    Alternative: Use Pastebin or similar services
    """
    
    def __init__(self):
        self.github_api = "https://api.github.com/gists"
        
    async def create_campaign_document(
        self,
        campaign_name: str,
        campaign_data: Dict[str, Any],
        base_url: str = None
    ) -> Dict[str, str]:
        """
        Create a shareable campaign document
        
        Args:
            campaign_name: Name of the campaign
            campaign_data: Campaign details
            base_url: Base URL for document service
            
        Returns:
            Dict with document URLs
        """
        try:
            # Use configured base URL if not provided
            if base_url is None:
                base_url = settings.app_base_url
            
            # Generate markdown content
            markdown_content = self._generate_markdown(campaign_name, campaign_data)
            
            # Generate unique document ID
            import hashlib
            doc_id = hashlib.md5(f"{campaign_name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
            
            # Save to local storage via API
            save_result = await self._save_to_local_storage(doc_id, markdown_content, campaign_data)
            
            if save_result:
                return {
                    "success": True,
                    "doc_url": f"{base_url}/documents/{doc_id}/view",
                    "raw_url": f"{base_url}/documents/{doc_id}",
                    "doc_id": doc_id,
                    "format": "markdown"
                }
            
            # Fallback: Return content directly
            return {
                "success": False,
                "content": markdown_content,
                "format": "markdown"
            }
            
        except Exception as e:
            logger.error(f"Failed to create document: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": markdown_content if 'markdown_content' in locals() else ""
            }
    
    async def _save_to_local_storage(
        self,
        doc_id: str,
        content: str,
        campaign_data: Dict[str, Any] = None
    ) -> bool:
        """
        Save document to local storage via API endpoint
        """
        try:
            # Import here to avoid circular dependency
            from app.routes.documents import document_store, campaign_store
            
            # Save markdown content
            document_store[doc_id] = content
            
            # Save campaign data for HTML rendering
            if campaign_data:
                campaign_store[doc_id] = campaign_data
            
            logger.info(f"✅ Document saved locally: {doc_id}")
            return True
                    
        except Exception as e:
            logger.error(f"Local storage error: {str(e)}")
            return False
    
    def _generate_markdown(
        self,
        campaign_name: str,
        campaign_data: Dict[str, Any]
    ) -> str:
        """
        Generate campaign document in Markdown format
        """
        product = campaign_data.get('product', campaign_name)
        budget = campaign_data.get('budget', {})
        schedule = campaign_data.get('schedule', {})
        platforms = campaign_data.get('platforms_strategy', {})
        kpis = campaign_data.get('kpis', [])
        recommendations = campaign_data.get('recommendations', [])
        
        content = campaign_data.get('campaign_content', '')
        
        markdown = f"""# 🎯 Marketing Campaign Plan
## {product}

**Created:** {datetime.now().strftime('%B %d, %Y')}  
**Status:** Ready to Execute

---

## 📊 Campaign Overview

### Budget
**Total Budget:** {budget.get('total_budget', 'Rp 5.000.000')}

"""
        
        # Budget Allocation
        allocation = budget.get('allocation', {})
        if allocation:
            markdown += "### Budget Allocation\n\n"
            for channel, data in allocation.items():
                if isinstance(data, dict):
                    percentage = data.get('percentage', '')
                    amount = data.get('amount', '')
                    markdown += f"- **{channel.replace('_', ' ').title()}**: {percentage} ({amount})\n"
            markdown += "\n"
        
        # Duration
        duration = schedule.get('duration_days', 30)
        markdown += f"### Duration\n**{duration} days** campaign\n\n"
        
        # Campaign Schedule
        phases = schedule.get('phases', [])
        if phases:
            markdown += "## 📅 Campaign Schedule\n\n"
            for phase in phases:
                week = phase.get('week', '')
                phase_name = phase.get('phase', '')
                activities = phase.get('activities', '')
                markdown += f"### Week {week}: {phase_name}\n"
                if activities:
                    markdown += f"{activities}\n\n"
        
        # Platform Strategy
        if platforms:
            markdown += "## 🚀 Platform Strategy\n\n"
            for platform, strategy in platforms.items():
                markdown += f"### {platform}\n{strategy}\n\n"
        
        # Campaign Content/Messaging
        if content:
            try:
                import json
                content_json = json.loads(content)
                tagline = content_json.get('tagline', '')
                messaging = content_json.get('messaging', [])
                cta = content_json.get('cta', '')
                
                markdown += "## 💬 Campaign Messaging\n\n"
                if tagline:
                    markdown += f"**Tagline:** {tagline}\n\n"
                if messaging:
                    markdown += "**Key Messages:**\n"
                    for msg in messaging:
                        markdown += f"- {msg}\n"
                    markdown += "\n"
                if cta:
                    markdown += f"**Call to Action:** {cta}\n\n"
            except:
                pass
        
        # KPIs
        if kpis:
            markdown += "## 📈 Key Performance Indicators\n\n"
            for kpi in kpis:
                markdown += f"- {kpi}\n"
            markdown += "\n"
        
        # Recommendations
        if recommendations:
            markdown += "## 💡 Recommendations\n\n"
            for rec in recommendations:
                markdown += f"- {rec}\n"
            markdown += "\n"
        
        # Footer
        markdown += """---

## 📋 Next Steps

1. **Review** this campaign plan with your team
2. **Adjust** budget and timeline as needed
3. **Create** content calendar based on schedule
4. **Set up** tracking in Google Sheets/Analytics
5. **Launch** campaign and monitor KPIs daily

---

*Generated by TrendScout AI Marketing Agent*  
*Need changes? Ask the AI to regenerate with different parameters*
"""
        
        return markdown


# Global instance
document_service = DocumentService()
