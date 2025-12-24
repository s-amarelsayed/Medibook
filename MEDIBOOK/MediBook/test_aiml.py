import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

api_key = os.environ.get('AIML_API_KEY')
print(f"API Key: {api_key}")

if api_key:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Try simpler payload first
    payload = {
        "model": "gpt-4o-mini",  # Try a different model
        "messages": [
            {"role": "user", "content": "Hello, what causes headaches?"}
        ]
    }
    
    try:
        print("\nSending request to AIML API...")
        response = requests.post(
            "https://api.aimlapi.com/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS!\n")
            print(result['choices'][0]['message']['content'])
        else:
            print(f"\n❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
else:
    print("❌ No API key")
