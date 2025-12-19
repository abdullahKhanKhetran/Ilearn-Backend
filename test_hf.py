import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv("HF_API_KEY")

if not API_KEY:
    print("❌ ERROR: HF_API_KEY not found in .env file")
    print("Please add: HF_API_KEY=hf_your_key_here")
    print("Get your key from: https://huggingface.co/settings/tokens")
    exit(1)

print(f"✓ API Key loaded (length: {len(API_KEY)})")
print("\n" + "="*60)
print("Testing HuggingFace Router API")
print("="*60)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ----------------------
# Test 1: Embedding (unchanged)
# ----------------------
print("\n[1/2] Testing Embeddings...")
embed_url = "https://router.huggingface.co/hf-inference/models/BAAI/bge-small-en-v1.5"

response = requests.post(
    embed_url,
    headers=headers,
    json={"inputs": "test", "options": {"wait_for_model": True}},
    timeout=30
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    vec = data[0] if isinstance(data[0], list) else data
    print(f"✓ Embeddings working! Dimension: {len(vec)}")
else:
    print(f"✗ Error: {response.text}")

# ----------------------
# Test 2: LLM using DeepSeek
# ----------------------
print("\n[2/2] Testing LLM (DeepSeek)...")

llm_url = "https://router.huggingface.co/v1/chat/completions"

payload = {
    "model": "deepseek-ai/DeepSeek-V3.2",  # Remove :novita if using chat API
    "messages": [
        {"role": "user", "content": "What is the capital of France?"}
    ]
}

response = requests.post(llm_url, headers=headers, json=payload, timeout=60)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    # Hugging Face chat API returns a list of choices
    print(f"✓ LLM working! Response: {data['choices'][0]['message']['content']}")
else:
    print(f"✗ Error: {response.text}")

print("\n" + "="*60)
print("✓ All tests complete!")
print("="*60)
