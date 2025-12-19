import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # HuggingFace API Configuration
    HF_API_KEY = os.getenv("HF_API_KEY")
    if not HF_API_KEY:
        raise ValueError("HF_API_KEY must be set in .env file")
    
    # Model Configuration (using HuggingFace Chat Completions API)
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-ai/DeepSeek-V3.2:novita")
    
    # HuggingFace API endpoints
    HF_ROUTER_ENDPOINT = "https://router.huggingface.co/hf-inference/models"
    HF_CHAT_COMPLETIONS_ENDPOINT = "https://router.huggingface.co/v1/chat/completions"
    
    # Data Paths
    STUDENT_DATA_PATH = "./data/student_data.json"
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./vector_store")
    
    # Performance Thresholds
    FANTASTIC_THRESHOLD = 85  # Average marks above this = fantastic
    AVERAGE_THRESHOLD = 60    # Between 60-85 = average
    # Below 60 = below average
    
    # Attendance Thresholds
    GOOD_ATTENDANCE = 80
    LOW_ATTENDANCE = 70

config = Config()