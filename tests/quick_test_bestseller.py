"""Quick test for bestseller feature"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.intent_classifier import IntentClassifier

async def test_intent():
    """Test intent classification for bestseller queries"""
    
    print("="*70)
    print("TESTING INTENT CLASSIFICATION FOR BESTSELLER QUERIES")
    print("="*70)
    print()
    
    classifier = IntentClassifier()
    
    queries = [
        "Carikan produk yang paling laris",
        "Produk apa yang bestseller?",
        "Tampilkan produk fashion terlaris",
        "Cari produk elektronik yang paling banyak terjual",
        "Produk skincare terlaris di Shopee"
    ]
    
    for query in queries:
        print(f"Query: \"{query}\"")
        
        result = await classifier.classify(query)
        
        print(f"  ✓ Intent: {result['intent']}")
        print(f"  ✓ Confidence: {result['confidence']:.2f}")
        print(f"  ✓ Parameters: {result.get('parameters', {})}")
        
        # Check if classified correctly
        if result['intent'] == 'find_bestsellers':
            print(f"  ✅ CORRECT - Detected as find_bestsellers")
        else:
            print(f"  ⚠️  UNEXPECTED - Got {result['intent']} instead of find_bestsellers")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_intent())
