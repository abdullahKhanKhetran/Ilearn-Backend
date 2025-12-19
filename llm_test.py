import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HF_API_KEY")
# Use the value from your environment variables, or specify directly
# LLM_MODEL = os.getenv("LLM_MODEL", "google/gemma-2b-it")  # Default to gemma-2b-it

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 🔥 Correct Hugging Face Inference Endpoint URL
llm_url = "https://router.huggingface.co/v1/chat/completions"

response = requests.post(
    llm_url,
    headers=headers,
    json={
        "inputs": "Say hi in one short sentence",
        "parameters": {"max_new_tokens": 40, "temperature": 0.7},
        "options": {"wait_for_model": True}
    },
    timeout=60
)

print("Status:", response.status_code)

if response.status_code == 200:
    try:
        data = response.json()
        if isinstance(data, list):
            text = data[0].get("generated_text") or data[0].get("text") or str(data[0])
        else:
            text = str(data)
        print(f"✅ LLM working! Response: {text[:100]}")
    except Exception as e:
        print("❌ JSON parse error:", e)
else:
    print(f"✗ ERROR: {response.status_code} {response.text}")