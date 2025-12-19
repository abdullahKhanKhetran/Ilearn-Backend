import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HF_API_KEY")
API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("=" * 60)
print("Testing DeepSeek via HuggingFace Chat Completions API")
print("=" * 60)

# Test DeepSeek
print("\nTesting DeepSeek LLM...")
payload = {
    "model": "deepseek-ai/DeepSeek-V3.2:novita",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "What is 2+2? Answer in one sentence."
        }
    ],
    "max_tokens": 50,
    "temperature": 0.7
}

response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    message = result["choices"][0]["message"]["content"]
    print(f"✓ DeepSeek working!")
    print(f"Response: {message}")
else:
    print(f"✗ Error: {response.text}")

print("\n" + "=" * 60)
print("If this works, your chatbot will work too!")
print("=" * 60)