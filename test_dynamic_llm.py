#!/usr/bin/env python3
"""
Test script for the updated HypermodeLLM with dynamic responses
"""

from hypermode_llm import HypermodeLLM

def test_dynamic_llm():
    """Test the HypermodeLLM with dynamic knowledge base."""
    print("🧪 Testing Dynamic HypermodeLLM")
    print("=" * 40)
    
    llm = HypermodeLLM()
    
    test_queries = [
        "What are the cheapest parking options?",
        "Find parking near Union Square",
        "Which garages are open 24/7?",
        "Show me EV charging parking",
        "What features do garages have?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 50)
        
        try:
            response = llm._call(query)
            # Show first 300 characters of response
            print(response[:300] + "..." if len(response) > 300 else response)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Dynamic LLM testing completed!")

if __name__ == "__main__":
    test_dynamic_llm()
