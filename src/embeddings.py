import requests
import time
from typing import List
from src.config import config

class EmbeddingModel:
    def __init__(self):
        """Use BAAI/bge-small-en-v1.5 model (384 dimensions)"""
        self.api_url = "https://router.huggingface.co/hf-inference/models/BAAI/bge-small-en-v1.5"
        self.headers = {
            "Authorization": f"Bearer {config.HF_API_KEY}",
            "Content-Type": "application/json"
        }
        print(f"Using BAAI/bge-small-en-v1.5 for embeddings")
    
    def _call_api(self, text: str, retries: int = 3):
        """Call API with retry"""
        for attempt in range(retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json={"inputs": text, "options": {"wait_for_model": True}},
                    timeout=30
                )
                
                if response.status_code == 503:
                    print(f"Model loading... wait 20s")
                    time.sleep(20)
                    continue
                
                response.raise_for_status()
                result = response.json()
                
                # Extract embedding
                if isinstance(result, list):
                    if isinstance(result[0], list):
                        return result[0]
                    return result
                
                raise Exception(f"Bad format: {result}")
                
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                time.sleep(5)
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding"""
        return self._call_api(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate multiple embeddings"""
        embeddings = []
        for i, text in enumerate(texts):
            print(f"Embedding {i+1}/{len(texts)}...")
            embedding = self.embed_text(text)
            embeddings.append(embedding)
            time.sleep(1)
        return embeddings

_embedding_model = None

def get_embedding_model() -> EmbeddingModel:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model