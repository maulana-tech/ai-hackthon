"""
Utility untuk load pre-scraped Shopee supplier data

Data format:
[
  {
    "network": "Shopee",
    "keyword": "keyword",
    "title": "Product/Shop Title",
    "description": "Description with email",
    "url": "Shopee URL",
    "email": "contact@email.com",
    "proxyGroups": ["RESIDENTIAL"]
  }
]
"""
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ShopeeDataLoader:
    """Load and filter pre-scraped Shopee supplier data"""
    
    def __init__(self, data_file: str = "sample_shopee_data.json"):
        """
        Initialize loader with data file
        
        Args:
            data_file: Path to JSON file with Shopee data
        """
        # Try multiple paths
        possible_paths = [
            Path(data_file),
            Path.cwd() / data_file,
            Path(__file__).parent.parent.parent / data_file,  # Project root
        ]
        
        self.data_file = None
        for path in possible_paths:
            if path.exists():
                self.data_file = path
                break
        
        self.data = []
        
        if self.data_file and self.data_file.exists():
            self._load_data()
        else:
            logger.warning(f"Shopee data file not found in any of: {[str(p) for p in possible_paths]}")
    
    def _load_data(self):
        """Load data from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            logger.info(f"✅ Loaded {len(self.data)} Shopee suppliers from {self.data_file}")
        except Exception as e:
            logger.error(f"Failed to load Shopee data: {str(e)}")
            self.data = []
    
    def search(
        self,
        keyword: str,
        limit: int = 10,
        min_rating: float = 4.0
    ) -> List[Dict[str, Any]]:
        """
        Search suppliers by keyword
        
        Args:
            keyword: Search keyword
            limit: Maximum results
            min_rating: Minimum rating (not used for pre-scraped data)
            
        Returns:
            List of matching suppliers
        """
        if not self.data:
            return []
        
        keyword_lower = keyword.lower()
        results = []
        
        for item in self.data:
            # Search in title, description, and keyword fields
            title = item.get('title', '').lower()
            desc = item.get('description', '').lower()
            item_keyword = item.get('keyword', '').lower()
            
            if (keyword_lower in title or 
                keyword_lower in desc or 
                keyword_lower in item_keyword or
                any(word in title for word in keyword_lower.split())):
                
                # Convert to standard format
                supplier = {
                    "name": item.get("title", "N/A"),
                    "title": item.get("title", "N/A"),
                    "description": item.get("description", "")[:200] + "...",
                    "url": item.get("url", ""),
                    "product_url": item.get("url", ""),
                    "email": item.get("email", ""),
                    "supplier_email": item.get("email", ""),
                    "keyword": item.get("keyword", ""),
                    "platform": "Shopee",
                    "rating": 4.5,  # Default good rating
                    "shop_rating": 4.5,
                    "verified": True if item.get("email") else False
                }
                results.append(supplier)
                
                if len(results) >= limit:
                    break
        
        logger.info(f"🔍 Found {len(results)} Shopee suppliers for '{keyword}'")
        return results
    
    def get_all(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all suppliers"""
        return self.search("", limit=limit)
    
    def filter_by_email(self, has_email: bool = True) -> List[Dict[str, Any]]:
        """Filter suppliers by email availability"""
        if has_email:
            return [item for item in self.data if item.get("email")]
        else:
            return [item for item in self.data if not item.get("email")]


# Singleton instance
_loader = None

def get_shopee_data_loader(data_file: Optional[str] = None) -> ShopeeDataLoader:
    """Get singleton ShopeeDataLoader instance"""
    global _loader
    if _loader is None or data_file:
        _loader = ShopeeDataLoader(data_file or "sample_shopee_data.json")
    return _loader
