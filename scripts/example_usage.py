#!/usr/bin/env python3
"""
Example usage of TrendScout Supplier Connector API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def example_1_analyze_trend():
    """Example 1: Analyze trending products"""
    print("\n" + "="*60)
    print("Example 1: Analyze Trending Products")
    print("="*60)
    
    url = f"{BASE_URL}/api/agent/analyze-trend"
    
    payload = {
        "query": "smart home devices",
        "user_id": "demo_user",
        "region": "global",
        "limit": 3
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Success!")
        print(f"Found {len(data['data']['products'])} trending products:")
        
        for i, product in enumerate(data['data']['products'], 1):
            print(f"\n{i}. {product['name']}")
            print(f"   Trend Score: {product['trend_score']}/100")
            print(f"   Growth: +{product['growth_percentage']}%")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def example_2_find_suppliers():
    """Example 2: Find suppliers"""
    print("\n" + "="*60)
    print("Example 2: Find Suppliers")
    print("="*60)
    
    url = f"{BASE_URL}/api/agent/find-suppliers"
    
    payload = {
        "product_name": "wireless earbuds",
        "user_id": "demo_user",
        "location": "Jakarta",
        "min_rating": 4.0,
        "limit": 5
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Success!")
        print(f"Found {len(data['data']['suppliers'])} suppliers:")
        
        for i, supplier in enumerate(data['data']['suppliers'], 1):
            print(f"\n{i}. {supplier['store_name']}")
            print(f"   Location: {supplier['city']}")
            print(f"   Rating: {supplier['rating']}/5.0")
            print(f"   Price: Rp {supplier['price']:,.0f}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def example_3_full_workflow():
    """Example 3: Execute full workflow"""
    print("\n" + "="*60)
    print("Example 3: Full Workflow (Main Feature)")
    print("="*60)
    
    url = f"{BASE_URL}/api/agent/execute-workflow"
    
    params = {
        "query": "skincare products",
        "user_id": "demo_user",
        "quantity": 20,
        "region": "global",
        "location": "Jakarta",
        "auto_contact": False  # Set False untuk demo
    }
    
    print("\n⏳ Executing workflow... (this may take 20-30 seconds)")
    
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        data = response.json()['data']
        
        print("\n✅ Workflow completed!")
        print(f"\n📊 Job ID: {data['job_id']}")
        print(f"\n🔍 Trending Products: {len(data['trending_products'])}")
        
        for product in data['trending_products']:
            print(f"  • {product['name']} (Score: {product['trend_score']}/100)")
        
        print(f"\n🏪 Suppliers: {len(data['suppliers'])}")
        
        for supplier in data['suppliers']:
            print(f"  • {supplier['store_name']} ({supplier['city']}) - Rp {supplier['price']:,.0f}")
        
        print("\n📋 Summary:")
        print(data['summary'])
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def example_4_check_status():
    """Example 4: Check job status"""
    print("\n" + "="*60)
    print("Example 4: Check Job Status")
    print("="*60)
    
    job_id = input("Enter Job ID: ").strip()
    
    url = f"{BASE_URL}/api/agent/status/{job_id}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nStatus: {data['status']}")
        print(f"Progress: {data['progress']}%")
        print(f"Message: {data['message']}")
    else:
        print(f"❌ Error: {response.status_code}")

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def main():
    print("\n🤖 TrendScout Supplier Connector - API Examples")
    
    if not check_api_health():
        print("\n❌ API is not running!")
        print("Please start the server first:")
        print("  uv run python app/main.py")
        print("or:")
        print("  ./run.sh")
        return
    
    print("\n✅ API is running at", BASE_URL)
    
    while True:
        print("\n" + "="*60)
        print("Select example to run:")
        print("="*60)
        print("1. Analyze Trending Products")
        print("2. Find Suppliers")
        print("3. Full Workflow (Recommended)")
        print("4. Check Job Status")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-4): ").strip()
        
        if choice == "1":
            example_1_analyze_trend()
        elif choice == "2":
            example_2_find_suppliers()
        elif choice == "3":
            example_3_full_workflow()
        elif choice == "4":
            example_4_check_status()
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        else:
            print("Invalid choice!")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
