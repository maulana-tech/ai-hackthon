"""
Helper functions for BestsellerFinder Agent
"""
import json
import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.models.schemas import TrendingProduct

logger = logging.getLogger(__name__)


def _parse_number_string(text: str) -> int:
    """Parse number string like '1.2k' or '10rb' to int"""
    if not text:
        return 0
    
    text = str(text).lower().strip()
    
    # Handle Indonesian/international abbreviations
    multipliers = {
        'rb': 1000,      # ribu (thousand)
        'k': 1000,       # thousand
        'jt': 1000000,   # juta (million)
        'm': 1000000,    # million
    }
    
    # Extract number and suffix
    match = re.search(r'([\d.,]+)\s*([a-z]+)?', text)
    if match:
        number_str = match.group(1).replace('.', '').replace(',', '.')
        suffix = match.group(2) or ''
        
        try:
            number = float(number_str)
            multiplier = multipliers.get(suffix, 1)
            return int(number * multiplier)
        except ValueError:
            return 0
    
    return 0


async def load_suppliers_from_data_folder(category: Optional[str], limit: int) -> List[TrendingProduct]:
    """
    Load pre-scraped supplier data from data/suppliers/ folder
    
    This function reads JSON files from data/suppliers/ directory and converts
    them into TrendingProduct format for display.
    """
    try:
        logger.info(f"Loading supplier data from data/suppliers/ folder - category: {category}")
        
        data_folder = Path("data/suppliers")
        if not data_folder.exists():
            logger.warning(f"Data folder does not exist: {data_folder}")
            return []
        
        products = []
        
        # Read all JSON files in data/suppliers/
        for json_file in data_folder.glob("*.json"):
            try:
                logger.info(f"Reading {json_file.name}...")
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract product name from filename or data
                product_name = data.get('product', json_file.stem.replace('suppliers_', '').split('_')[0])
                suppliers = data.get('suppliers', [])
                
                # Convert each supplier to TrendingProduct format
                for supplier in suppliers[:limit]:
                    try:
                        # Extract info from supplier data
                        name = supplier.get('product_name', supplier.get('name', 'Unknown Product'))
                        price = supplier.get('price', 0)
                        location = supplier.get('location', supplier.get('city', 'Indonesia'))
                        
                        # Skip if category filter doesn't match (basic check)
                        if category and category.lower() not in name.lower() and category.lower() not in product_name.lower():
                            continue
                        
                        product = TrendingProduct(
                            name=name,
                            category=category or "General",
                            trend_score=75.0,  # Good score for pre-scraped verified suppliers
                            growth_percentage=50.0,
                            search_volume=500,  # Estimate
                            region="Indonesia",
                            platform=supplier.get('marketplace', 'Indonetwork'),
                            description=f"Supplier: {supplier.get('store_name', supplier.get('name', 'N/A'))} | Location: {location}",
                            image_url="",
                            price_range=f"Rp {price:,.0f}" if price > 0 else "Contact supplier",
                            keywords=[product_name],
                            rating=float(supplier.get('rating', 4.5)),
                            total_sold=supplier.get('minimum_order', 1) * 100,  # Estimate based on MOQ
                            review_count=50,  # Estimate
                            shop_name=supplier.get('store_name', supplier.get('name', 'N/A')),
                            shop_location=location,
                            product_url=supplier.get('url', ''),
                            is_official=supplier.get('verified', False)
                        )
                        
                        products.append(product)
                        
                        # Stop if we have enough products
                        if len(products) >= limit:
                            break
                    
                    except Exception as e:
                        logger.warning(f"Error parsing supplier: {str(e)}")
                        continue
                
                # Stop if we have enough products
                if len(products) >= limit:
                    break
                    
            except Exception as e:
                logger.warning(f"Error reading {json_file.name}: {str(e)}")
                continue
        
        logger.info(f"✅ Loaded {len(products)} products from supplier data")
        return products[:limit]
        
    except Exception as e:
        logger.error(f"Error loading supplier data from folder: {str(e)}")
        return []


def parse_tokopedia_item(item: Dict[str, Any], category: Optional[str], search_query: str) -> Optional[TrendingProduct]:
    """
    Parse Tokopedia item from Apify API response (with robust error handling)
    
    Expected fields from Apify jupri/tokopedia-scraper:
    - name or productName
    - price (can be dict or int/string)
    - rating or sellerRating
    - sold or totalSold
    - reviewCount
    - shopName or sellerName
    - shopLocation
    - url
    - image or imageUrl
    """
    try:
        # Extract fields with multiple possible keys
        name = item.get('name', item.get('productName', 'Unknown Product'))
        
        # Parse price (can be dict, string, or int)
        price_raw = item.get('price', item.get('priceInt', 0))
        if isinstance(price_raw, dict):
            # If price is a dict, try to get value from common keys
            price = float(price_raw.get('value', price_raw.get('amount', price_raw.get('price', 0))))
        elif isinstance(price_raw, str):
            # Clean string price
            price_clean = price_raw.replace('Rp', '').replace('.', '').replace(',', '').strip()
            price = float(price_clean) if price_clean else 0
        else:
            price = float(price_raw) if price_raw else 0
        
        # Parse rating (can be dict or float)
        rating_raw = item.get('rating', item.get('sellerRating', item.get('shopRating', 4.0)))
        if isinstance(rating_raw, dict):
            rating = float(rating_raw.get('value', rating_raw.get('rating', 4.0)))
        elif isinstance(rating_raw, str):
            rating = float(rating_raw) if rating_raw else 4.0
        else:
            rating = float(rating_raw) if rating_raw else 4.0
        
        # Parse total sold (can be dict or int)
        sold_raw = item.get('sold', item.get('totalSold', item.get('sales', 0)))
        if isinstance(sold_raw, dict):
            total_sold = int(sold_raw.get('value', sold_raw.get('count', 0)))
        elif isinstance(sold_raw, str):
            # Handle "1.2k" format
            total_sold = _parse_number_string(sold_raw)
        else:
            total_sold = int(sold_raw) if sold_raw else 0
        
        # Parse review count
        review_raw = item.get('reviewCount', item.get('review', 0))
        if isinstance(review_raw, dict):
            review_count = int(review_raw.get('value', review_raw.get('count', 0)))
        elif isinstance(review_raw, str):
            review_count = _parse_number_string(review_raw)
        else:
            review_count = int(review_raw) if review_raw else 0
        
        shop_name = item.get('shopName', item.get('sellerName', 'Unknown Shop'))
        shop_location = item.get('shopLocation', item.get('location', 'Indonesia'))
        product_url = item.get('url', item.get('productUrl', ''))
        image_url = item.get('image', item.get('imageUrl', ''))
        is_official = item.get('isOfficial', item.get('isOfficialStore', False))
        
        # Calculate trend score
        sold_score = min(total_sold / 100, 100)  # Normalize to 0-100
        rating_score = (rating / 5.0) * 100
        review_score = min(review_count / 10, 100)
        official_bonus = 20 if is_official else 0
        
        trend_score = (
            sold_score * 0.4 +
            rating_score * 0.3 +
            review_score * 0.2 +
            official_bonus * 0.1
        )
        
        product = TrendingProduct(
            name=name,
            category=category or "General",
            trend_score=round(trend_score, 2),
            growth_percentage=50.0,
            search_volume=total_sold,
            region="Indonesia",
            platform="Tokopedia",
            description=f"{shop_name} | {shop_location}",
            image_url=image_url,
            price_range=f"Rp {price:,.0f}" if price > 0 else "Varies",
            keywords=[search_query],
            rating=rating,
            total_sold=total_sold,
            review_count=review_count,
            shop_name=shop_name,
            shop_location=shop_location,
            product_url=product_url,
            is_official=is_official
        )
        
        return product
        
    except Exception as e:
        logger.error(f"Error parsing Tokopedia item: {str(e)}")
        return None
