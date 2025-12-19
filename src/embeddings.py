import requests
import time
from typing import List
from src.config import config

class EmbeddingModel:
    def __init__(self):
        """Initialize the embedding model using HuggingFace Router API"""
        self.api_url = f"{config.HF_ROUTER_ENDPOINT}/{config.EMBEDDING_MODEL}"
        self.headers = {
            "Authorization": f"Bearer {config.HF_API_KEY}",
            "Content-Type": "application/json"
        }
        print(f"Using HuggingFace Router API for embeddings: {config.EMBEDDING_MODEL}")
        print("No models will be downloaded to your device!")
    
    def _call_api(self, payload: dict, retries: int = 3) -> dict:
        """Call HuggingFace Router API with retry logic"""
        for attempt in range(retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 503:
                    # Model is loading, wait and retry
                    print(f"Model is loading... waiting 20 seconds (attempt {attempt + 1}/{retries})")
                    time.sleep(20)
                    continue
                
                if response.status_code != 200:
                    print(f"API Error {response.status_code}: {response.text}")
                    
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    raise Exception(f"API call failed after {retries} attempts: {str(e)}")
                time.sleep(5)
        
        raise Exception("Failed to get response from API")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for a single text"""
        payload = {
            "inputs": text,
            "options": {"wait_for_model": True}
        }
        result = self._call_api(payload)
        
        # HuggingFace Router returns embeddings as a flat list
        if isinstance(result, list):
            # If it's a number list, return it directly
            if len(result) > 0 and isinstance(result[0], (int, float)):
                return result
            # If nested (batch), take first
            elif len(result) > 0 and isinstance(result[0], list):
                return result[0]
        
        raise Exception(f"Unexpected response format: {type(result)}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        for i, text in enumerate(texts):
            print(f"Embedding document {i+1}/{len(texts)}...")
            embedding = self.embed_text(text)
            embeddings.append(embedding)
            time.sleep(1)  # Rate limiting
        return embeddings

# Singleton instance
_embedding_model = None

def get_embedding_model() -> EmbeddingModel:
    """Get or create the embedding model instance"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model