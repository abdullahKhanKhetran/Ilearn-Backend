from pydantic import BaseModel, Field
from typing import Optional, List

class Message(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    student_id: str = Field(..., description="Student ID to query about")
    message: str = Field(..., description="User's message")
    conversation_history: Optional[List[Message]] = Field(default=[], description="Previous conversation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "S001",
                "message": "How is this student performing?",
                "conversation_history": []
            }
        }

class ChatResponse(BaseModel):
    student_id: str
    message: str
    response: str
    performance_category: Optional[str] = None
    conversation_history: List[Message]
    suggestions: List[str] = Field(default=[], description="Suggested follow-up questions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "S001",
                "message": "How is this student performing?",
                "response": "Ahmed Khan is performing well overall...",
                "performance_category": "Average",
                "conversation_history": [],
                "suggestions": ["What subjects need improvement?", "Show attendance details"]
            }
        }

class HealthResponse(BaseModel):
    status: str
    message: str