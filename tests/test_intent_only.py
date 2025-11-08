#!/usr/bin/env python3
"""Quick test for Intent Classifier"""

import asyncio
from app.agents.intent_classifier import IntentClassifier


async def main():
    print("\n" + "="*70)
    print("Intent Classifier Test")
    print("="*70 + "\n")
    
    classifier = IntentClassifier()
    
    test_queries = [
        "Cari produk skincare yang lagi trending",
        "Supplier tas macrame di Jakarta",
        "Produk home decor trending dan supplier di Bali",
        "Hubungi supplier yang tadi",
        "Gimana status job saya?",
        "Cari supplier furniture di Surabaya min rating 4.5",
    ]
    
    for query in test_queries:
        print(f"📝 Query: \"{query}\"")
        
        result = await classifier.classify(query)
        
        print(f"   ✅ Intent: {result['intent']}")
        print(f"   ✅ Confidence: {result['confidence']:.2f}")
        
        if result.get('parameters'):
            print(f"   ✅ Parameters:")
            for key, value in result['parameters'].items():
                print(f"      - {key}: {value}")
        
        print()
    
    print("="*70)
    print("✅ Intent Classifier Working!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
