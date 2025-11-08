"""
Mock Data - Fallback data when API limits are hit
"""
from typing import List
from app.models.schemas import TrendingProduct

def get_mock_bestsellers(category: str = "elektronik", limit: int = 5) -> List[TrendingProduct]:
    """
    Get mock bestseller data as fallback when APIs are rate limited
    
    This provides realistic demo data based on actual Indonesian marketplace trends
    """
    
    electronics_data = [
        {
            "name": "Xiaomi Redmi Earbuds 3 Pro TWS",
            "category": "Elektronik",
            "trend_score": 92.5,
            "growth_percentage": 45.0,
            "search_volume": 15234,
            "region": "Indonesia",
            "platform": "Tokopedia",
            "description": "TWS earbuds berkualitas dengan ANC dan audio berkualitas tinggi",
            "price_range": "Rp 299,000",
            "keywords": ["earbuds", "tws", "xiaomi"],
            "rating": 4.8,
            "total_sold": 15234,
            "review_count": 3421,
            "shop_name": "Xiaomi Official Store",
            "shop_location": "Jakarta Pusat",
            "is_official": True
        },
        {
            "name": "Fantech Gaming Mouse MH88 RGB",
            "category": "Elektronik",
            "trend_score": 88.3,
            "growth_percentage": 38.0,
            "search_volume": 12890,
            "region": "Indonesia",
            "platform": "Shopee",
            "description": "Gaming mouse RGB dengan DPI tinggi untuk gaming profesional",
            "price_range": "Rp 159,000",
            "keywords": ["gaming", "mouse", "rgb"],
            "rating": 4.7,
            "total_sold": 12890,
            "review_count": 2856,
            "shop_name": "Fantech Official",
            "shop_location": "Bandung",
            "is_official": True
        },
        {
            "name": "Logitech Webcam C920 HD Pro",
            "category": "Elektronik",
            "trend_score": 85.7,
            "growth_percentage": 42.0,
            "search_volume": 8543,
            "region": "Indonesia",
            "platform": "Tokopedia",
            "description": "Webcam HD untuk streaming dan video call berkualitas",
            "price_range": "Rp 1,299,000",
            "keywords": ["webcam", "hd", "logitech"],
            "rating": 4.9,
            "total_sold": 8543,
            "review_count": 1923,
            "shop_name": "Logitech Store",
            "shop_location": "Jakarta Selatan",
            "is_official": True
        },
        {
            "name": "Xiaomi Power Bank 20000mAh",
            "category": "Elektronik",
            "trend_score": 83.2,
            "growth_percentage": 35.0,
            "search_volume": 23450,
            "region": "Indonesia",
            "platform": "Shopee",
            "description": "Power bank kapasitas besar dengan fast charging",
            "price_range": "Rp 189,000",
            "keywords": ["powerbank", "xiaomi", "20000mah"],
            "rating": 4.6,
            "total_sold": 23450,
            "review_count": 5234,
            "shop_name": "Xiaomi Mall",
            "shop_location": "Jakarta",
            "is_official": True
        },
        {
            "name": "SanDisk USB Flash Drive 64GB",
            "category": "Elektronik",
            "trend_score": 79.8,
            "growth_percentage": 30.0,
            "search_volume": 18230,
            "region": "Indonesia",
            "platform": "Tokopedia",
            "description": "USB flash drive berkecepatan tinggi USB 3.0",
            "price_range": "Rp 89,000",
            "keywords": ["usb", "flashdrive", "sandisk"],
            "rating": 4.5,
            "total_sold": 18230,
            "review_count": 3567,
            "shop_name": "SanDisk Official",
            "shop_location": "Surabaya",
            "is_official": True
        }
    ]
    
    fashion_data = [
        {
            "name": "Gamis Syari Set Khimar",
            "category": "Fashion",
            "trend_score": 90.2,
            "growth_percentage": 48.0,
            "search_volume": 23450,
            "region": "Indonesia",
            "platform": "Shopee",
            "description": "Gamis syari dengan khimar matching, bahan premium",
            "price_range": "Rp 189,000",
            "keywords": ["gamis", "syari", "muslim"],
            "rating": 4.8,
            "total_sold": 23450,
            "review_count": 5234,
            "shop_name": "Muslim Fashion Store",
            "shop_location": "Bandung",
            "is_official": True
        },
        {
            "name": "Kemeja Flanel Pria Lengan Panjang",
            "category": "Fashion",
            "trend_score": 85.6,
            "growth_percentage": 40.0,
            "search_volume": 18230,
            "region": "Indonesia",
            "platform": "Tokopedia",
            "description": "Kemeja flanel premium untuk casual dan hangout",
            "price_range": "Rp 89,000",
            "keywords": ["kemeja", "flanel", "pria"],
            "rating": 4.6,
            "total_sold": 18230,
            "review_count": 3567,
            "shop_name": "Men Fashion ID",
            "shop_location": "Jakarta",
            "is_official": False
        }
    ]
    
    beauty_data = [
        {
            "name": "Somethinc Niacinamide Serum",
            "category": "Beauty",
            "trend_score": 94.5,
            "growth_percentage": 55.0,
            "search_volume": 35678,
            "region": "Indonesia",
            "platform": "Tokopedia",
            "description": "Serum niacinamide untuk mencerahkan kulit",
            "price_range": "Rp 89,000",
            "keywords": ["serum", "niacinamide", "skincare"],
            "rating": 4.9,
            "total_sold": 35678,
            "review_count": 8234,
            "shop_name": "Somethinc Official",
            "shop_location": "Jakarta",
            "is_official": True
        }
    ]
    
    # Select data based on category
    if "elektronik" in category.lower() or "electronic" in category.lower():
        data_list = electronics_data
    elif "fashion" in category.lower() or "pakaian" in category.lower():
        data_list = fashion_data
    elif "beauty" in category.lower() or "kecantikan" in category.lower():
        data_list = beauty_data
    else:
        # Default to electronics
        data_list = electronics_data
    
    # Convert to TrendingProduct objects
    products = []
    for data in data_list[:limit]:
        products.append(TrendingProduct(**data))
    
    return products
