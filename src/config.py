import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("PORT", 8000))
    
    # HuggingFace API Configuration
    HF_API_KEY = os.getenv("HF_API_KEY")
    if not HF_API_KEY:
        raise ValueError("HF_API_KEY must be set in .env file")
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    
    # Model Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-ai/DeepSeek-V3.2:novita")
    
    # HuggingFace API endpoints
    HF_ROUTER_ENDPOINT = "https://router.huggingface.co/hf-inference/models"
    HF_CHAT_COMPLETIONS_ENDPOINT = "https://router.huggingface.co/v1/chat/completions"
    
    # Data Paths (for reference/migration only)
    STUDENT_DATA_PATH = "./data/student_data.json"
    
    # Performance Thresholds
    FANTASTIC_THRESHOLD = 85
    AVERAGE_THRESHOLD = 60
    
    # Attendance Thresholds
    GOOD_ATTENDANCE = 80
    LOW_ATTENDANCE = 70

config = Config()