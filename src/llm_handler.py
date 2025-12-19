import requests
import time
from typing import List, Dict
from src.config import config

class LLMHandler:
    def __init__(self):
        """Initialize the LLM using HuggingFace Chat Completions API (OpenAI-compatible)"""
        self.api_url = config.HF_CHAT_COMPLETIONS_ENDPOINT
        self.headers = {
            "Authorization": f"Bearer {config.HF_API_KEY}",
            "Content-Type": "application/json"
        }
        self.model = config.LLM_MODEL
        print(f"Using HuggingFace Chat Completions API for LLM: {config.LLM_MODEL}")
        print("No models will be downloaded to your device!")
    
    def create_conversation_messages(
        self, 
        current_message: str, 
        context: str, 
        history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Create OpenAI-compatible messages array with history"""
        
        system_prompt = f"""You are Zeeshan's Bot, an educational AI assistant specializing in student performance analysis. 

Your personality:
- Friendly, conversational, and professional
- Handle greetings naturally (hi, hello, thanks, bye)
- Politely guide conversations toward student performance when appropriate
- Always maintain context from previous messages

Available Student Data:
{context}

Your responsibilities:
1. Respond naturally to greetings and casual conversation
2. When appropriate, gently transition to discussing the student's performance
3. Analyze student performance: Fantastic (≥85% + good attendance), Average (60-85%), or Below Average (<60%)
4. Provide specific, actionable improvement suggestions
5. Reference concrete data (marks, attendance, subjects)
6. Answer follow-up questions using conversation history
7. Be encouraging and supportive

Example interactions:
- User: "Hi" → You: "Hi there! I'm Zeeshan's Bot. I'm here to help analyze {context.split('Name: ')[1].split('\\n')[0] if 'Name:' in context else 'student'} performance. What would you like to know?"
- User: "How are you?" → You: "I'm doing great, thanks! Ready to discuss student performance whenever you are."
- User: "Thanks" → You: "You're welcome! Let me know if you need anything else about the student's performance."

Always be helpful, natural, and student-focused."""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current message
        messages.append({"role": "user", "content": current_message})
        
        return messages
    
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using HuggingFace Chat Completions API"""
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.95
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 503:
                    print(f"Model is loading... waiting 20 seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(20)
                    continue
                
                if response.status_code != 200:
                    print(f"API Error {response.status_code}: {response.text}")
                
                response.raise_for_status()
                result = response.json()
                
                # Extract message from OpenAI-compatible response
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0].get("message", {})
                    content = message.get("content", "")
                    return content.strip()
                
                return "Unable to generate response. Please try again."
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    return f"Error generating response: {str(e)}"
                print(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(5)
        
        return "Failed to generate response after multiple attempts."
    
    def generate_suggestions(self, student_data: Dict, conversation_context: str) -> List[str]:
        """Generate contextual follow-up suggestions"""
        suggestions = []
        
        # Parse student performance
        avg_marks = sum(subj['marks'] for subj in student_data['subjects'].values()) / len(student_data['subjects'])
        attendance = student_data['attendance']
        
        # Context-aware suggestions
        if avg_marks < 60:
            suggestions.append("What specific help does this student need?")
            suggestions.append("Which subjects should we focus on first?")
        elif avg_marks >= 85:
            suggestions.append("What are the student's strongest skills?")
            suggestions.append("Any suggestions for advanced learning?")
        else:
            suggestions.append("How can we improve performance?")
            suggestions.append("What are the improvement areas?")
        
        if attendance < 75:
            suggestions.append("Why is attendance low?")
        
        # General suggestions
        suggestions.append("Compare performance across all subjects")
        suggestions.append("Show detailed attendance records")
        
        return suggestions[:4]  # Return top 4 suggestions

# Singleton instance
_llm_handler = None

def get_llm_handler() -> LLMHandler:
    """Get or create the LLM handler instance"""
    global _llm_handler
    if _llm_handler is None:
        _llm_handler = LLMHandler()
    return _llm_handler