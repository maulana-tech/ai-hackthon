"""
Debug script to see actual markdown output from Indonetwork scraping
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.integrations.firecrawl_client import FirecrawlClient

async def test_single_product_scraping():
    """Test scraping a single Indonetwork product page"""
    
    firecrawl = FirecrawlClient()
    
    # Test URL from your output
    test_url = "https://www.indonetwork.co.id/product/botol-spray-pet-100ml-botol-pet-kosmetik-skincare-100-ml-7471062"
    
    print(f"🔍 Scraping: {test_url}\n")
    print("=" * 70)
    
    try:
        result = await firecrawl.scrape(
            test_url,
            formats=["markdown"]
        )
        
        if result and 'markdown' in result:
            markdown = result['markdown']
            
            print("MARKDOWN OUTPUT:")
            print("=" * 70)
            print(markdown)
            print("=" * 70)
            print()
            
            # Test regex patterns
            print("\nTESTING REGEX PATTERNS:")
            print("-" * 70)
            
            import re
            
            # Test company name extraction
            company_patterns = [
                r'(?:Perusahaan|Company)[:\s]+([^\n]+)',
                r'(?:Penjual|Seller)[:\s]+([^\n]+)',
                r'\*\*Tentang Perusahaan\*\*\s+([^\n]+)',
                r'##\s+([^#\n]+Supplier|[^#\n]+Toko|[^#\n]+PT\.)',
            ]
            
            print("\n1. Company Name Patterns:")
            for pattern in company_patterns:
                match = re.search(pattern, markdown, re.IGNORECASE)
                if match:
                    print(f"   ✅ Found: {match.group(1).strip()}")
                else:
                    print(f"   ❌ No match: {pattern}")
            
            # Test WhatsApp extraction
            whatsapp_patterns = [
                r'(?:WhatsApp|WA)[:\s]*([0-9\-\+\(\)\s]+)',
                r'WHATSAPP[:\s]*([0-9\-\+\(\)\s]+)',
                r'\+?62[\s\-]?\d{2,3}[\s\-]?\d{3,4}[\s\-]?\d{3,4}',
                r'0\d{2,3}[\s\-]?\d{3,4}[\s\-]?\d{3,4}'
            ]
            
            print("\n2. WhatsApp Patterns:")
            for pattern in whatsapp_patterns:
                match = re.search(pattern, markdown, re.IGNORECASE)
                if match:
                    print(f"   ✅ Found: {match.group(0).strip()}")
                else:
                    print(f"   ❌ No match: {pattern}")
            
            # Test location extraction
            location_patterns = [
                r'(?:Lokasi|Location|Alamat|Address)[:\s]*([^\n]+)',
                r'(?:Kota|City)[:\s]*([^\n]+)',
            ]
            
            print("\n3. Location Patterns:")
            for pattern in location_patterns:
                match = re.search(pattern, markdown, re.IGNORECASE)
                if match:
                    print(f"   ✅ Found: {match.group(1).strip()}")
                else:
                    print(f"   ❌ No match: {pattern}")
            
        else:
            print("❌ No markdown in result")
            print(f"Result keys: {result.keys() if result else 'None'}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_single_product_scraping())
