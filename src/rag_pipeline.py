from typing import Dict, Any, List
from src.vector_store import get_vector_store
from src.llm_handler import get_llm_handler
from src.utils import calculate_average_marks, categorize_performance

class RAGPipeline:
    def __init__(self):
        self.vector_store = get_vector_store()
        self.llm_handler = get_llm_handler()
    
    def process_query(
        self, 
        student_id: str, 
        message: str, 
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Process a conversational query using RAG pipeline"""
        
        if conversation_history is None:
            conversation_history = []
        
        # Step 1: Retrieve relevant context
        search_query = f"Student ID: {student_id} {message}"
        retrieved_docs, retrieved_metadata = self.vector_store.search(search_query, k=1)
        
        # Find the specific student
        student_data = None
        for metadata in retrieved_metadata:
            if metadata['student_id'] == student_id:
                student_data = metadata
                break
        
        if not student_data:
            # If student not found, provide helpful message
            return {
                "response": f"I don't have data for student ID {student_id}. Please select a student from the sidebar to begin our conversation.",
                "performance_category": None,
                "conversation_history": conversation_history,
                "suggestions": []
            }
        
        # Step 2: Determine performance category
        avg_marks = calculate_average_marks(student_data['subjects'])
        performance_category = categorize_performance(avg_marks, student_data['attendance'])
        
        # Step 3: Prepare context with student info
        context = retrieved_docs[0]
        
        # Step 4: Generate conversational response with history
        messages = self.llm_handler.create_conversation_messages(message, context, conversation_history)
        response = self.llm_handler.generate_response(messages)
        
        # Step 5: Update conversation history
        updated_history = conversation_history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response}
        ]
        
        # Step 6: Generate contextual suggestions
        suggestions = self.llm_handler.generate_suggestions(student_data, response)
        
        return {
            "response": response,
            "performance_category": performance_category,
            "conversation_history": updated_history,
            "suggestions": suggestions
        }

# Singleton instance
_rag_pipeline = None

def get_rag_pipeline() -> RAGPipeline:
    """Get or create the RAG pipeline instance"""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline