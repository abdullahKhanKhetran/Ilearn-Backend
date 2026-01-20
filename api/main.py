from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.models import ChatRequest, ChatResponse, HealthResponse
from src.rag_pipeline import get_rag_pipeline
from src.config import config
import uvicorn
import os

app = FastAPI(
    title="Student Performance Chatbot API",
    description="Conversational RAG-based chatbot for analyzing student performance",
    version="2.0.0"
)
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")
# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG pipeline on startup
@app.on_event("startup")
async def startup_event():
    try:
        print("Initializing RAG pipeline...")
        get_rag_pipeline()
        print("✅ API is ready!")
    except Exception as e:
        print(f"❌ Error initializing RAG pipeline: {e}")
        import traceback
        traceback.print_exc()
        # Don't crash the server - it can still serve health checks
        print("⚠️  Server will start but chat functionality may not work")

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Student Performance Chatbot API is running"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        message="All systems operational"
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Conversational chat endpoint with history
    
    Example request:
    ```json
    {
        "student_id": "S001",
        "message": "How is this student performing?",
        "conversation_history": []
    }
    ```
    
    Example with history:
    ```json
    {
        "student_id": "S001",
        "message": "What about Math specifically?",
        "conversation_history": [
            {"role": "user", "content": "How is this student performing?"},
            {"role": "assistant", "content": "Ahmed is performing well..."}
        ]
    }
    ```
    """
    try:
        rag_pipeline = get_rag_pipeline()
        
        # Convert Pydantic models to dicts for processing
        history = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]
        
        result = rag_pipeline.process_query(
            request.student_id, 
            request.message,
            history
        )
        
        # Convert history back to Message objects
        from src.models import Message
        conversation_messages = [
            Message(role=msg["role"], content=msg["content"]) 
            for msg in result["conversation_history"]
        ]
        
        return ChatResponse(
            student_id=request.student_id,
            message=request.message,
            response=result["response"],
            performance_category=result["performance_category"],
            conversation_history=conversation_messages,
            suggestions=result["suggestions"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/students")
async def list_students():
    """Get list of all available student IDs"""
    from src.utils import load_student_data
    students = load_student_data()
    return {
        "students": [
            {"student_id": s["student_id"], "name": s["name"]} 
            for s in students
        ]
    }

@app.post("/reset-conversation")
async def reset_conversation():
    """Reset conversation (for new chat session)"""
    return {
        "message": "Conversation reset. Start a new chat!",
        "conversation_history": []
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )