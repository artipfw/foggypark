#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_hypermode_api():
    api_key = os.getenv("HYPERMODE_API_KEY")
    model = os.getenv("HYPERMODE_MODEL")
    base_url = os.getenv("TEXT2VEC_OPENAI_BASE_URL")
    
    print(f"API Key: {api_key[:20]}..." if api_key else "API Key: None")
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    
    if not api_key or not model:
        print("❌ Missing HYPERMODE_API_KEY or HYPERMODE_MODEL in .env file")
        return False
    
    # Test different possible endpoints
    endpoints = [
        "https://api.hypermode.dev/inference",
        "https://api.hypermode.dev/v1/chat/completions",
        "https://models.hypermode.host/v1/chat/completions",
        f"{base_url}/chat/completions" if base_url else None
    ]
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Try OpenAI-compatible format first
    openai_payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello, this is a test. Please respond with 'API working correctly'."}],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    # Try original format
    original_payload = {
        "model": model,
        "prompt": "Hello, this is a test. Please respond with 'API working correctly'.",
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    for endpoint in endpoints:
        if not endpoint:
            continue
            
        print(f"\n🔄 Testing endpoint: {endpoint}")
        
        # Try OpenAI format first
        for payload_name, payload in [("OpenAI format", openai_payload), ("Original format", original_payload)]:
            try:
                print(f"  Trying {payload_name}...")
                response = requests.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                print(f"  Status Code: {response.status_code}")
                print(f"  Content-Type: {response.headers.get('content-type', 'N/A')}")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        print(f"  ✅ Success! Response: {result}")
                        return True
                    except Exception as e:
                        print(f"  ❌ JSON Parse Error: {e}")
                        print(f"  Response text (first 200 chars): {response.text[:200]}")
                else:
                    print(f"  ❌ HTTP Error: {response.status_code}")
                    print(f"  Response text (first 200 chars): {response.text[:200]}")
                    
            except Exception as e:
                print(f"  ❌ Connection Error: {e}")
    
    print("\n❌ All endpoints failed")
    return False

if __name__ == "__main__":
    test_hypermode_api()
