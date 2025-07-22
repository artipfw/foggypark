#!/usr/bin/env python3

from hypermode_llm import HypermodeLLM
from dotenv import load_dotenv

load_dotenv()

def test_hypermode_llm():
    try:
        print("🔄 Testing HypermodeLLM...")
        llm = HypermodeLLM()
        
        test_prompt = "I’m going to downtown San Francisco at 9 AM. What’s the best parking spot near the AWS Builder Loft?"
        print(f"Prompt: {test_prompt}")
        
        response = llm._call(test_prompt)
        print(f"✅ LLM Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ LLM Test Failed: {e}")
        return False

if __name__ == "__main__":
    test_hypermode_llm()
