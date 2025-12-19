import os
import pickle
import faiss
import numpy as np
from typing import List, Tuple, Dict, Any
from src.config import config
from src.embeddings import get_embedding_model
from src.utils import load_student_data, format_student_data_for_embedding

class VectorStore:
    def __init__(self):
        self.index = None
        self.documents = []
        self.metadata = []
        self.embedding_model = get_embedding_model()
        
    def create_index(self):
        """Create FAISS index from student data"""
        print("Loading student data...")
        students = load_student_data()
        
        print("Formatting student data for embedding...")
        texts = [format_student_data_for_embedding(student) for student in students]
        
        print("Generating embeddings...")
        embeddings = self.embedding_model.embed_texts(texts)
        embeddings_array = np.array(embeddings).astype('float32')
        
        print(f"Creating FAISS index with {len(embeddings)} documents...")
        dimension = embeddings_array.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings_array)
        
        self.documents = texts
        self.metadata = students
        
        print("Index created successfully!")
        
    def save_index(self):
        """Save FAISS index to disk"""
        os.makedirs(config.VECTOR_STORE_PATH, exist_ok=True)
        
        faiss.write_index(self.index, os.path.join(config.VECTOR_STORE_PATH, "index.faiss"))
        
        with open(os.path.join(config.VECTOR_STORE_PATH, "documents.pkl"), 'wb') as f:
            pickle.dump(self.documents, f)
        
        with open(os.path.join(config.VECTOR_STORE_PATH, "metadata.pkl"), 'wb') as f:
            pickle.dump(self.metadata, f)
        
        print(f"Index saved to {config.VECTOR_STORE_PATH}")
    
    def load_index(self):
        """Load FAISS index from disk"""
        index_path = os.path.join(config.VECTOR_STORE_PATH, "index.faiss")
        
        if not os.path.exists(index_path):
            print("Index not found. Creating new index...")
            self.create_index()
            self.save_index()
            return
        
        print("Loading existing index...")
        self.index = faiss.read_index(index_path)
        
        with open(os.path.join(config.VECTOR_STORE_PATH, "documents.pkl"), 'rb') as f:
            self.documents = pickle.load(f)
        
        with open(os.path.join(config.VECTOR_STORE_PATH, "metadata.pkl"), 'rb') as f:
            self.metadata = pickle.load(f)
        
        print("Index loaded successfully!")
    
    def search(self, query: str, k: int = 2) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Search for relevant documents"""
        query_embedding = np.array([self.embedding_model.embed_text(query)]).astype('float32')
        
        distances, indices = self.index.search(query_embedding, k)
        
        retrieved_docs = [self.documents[i] for i in indices[0]]
        retrieved_metadata = [self.metadata[i] for i in indices[0]]
        
        return retrieved_docs, retrieved_metadata

# Singleton instance
_vector_store = None

def get_vector_store() -> VectorStore:
    """Get or create the vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
        _vector_store.load_index()
    return _vector_store