import time
from typing import List, Tuple, Dict, Any, Optional
from supabase import create_client, Client
from src.config import config
from src.embeddings import get_embedding_model
from src.utils import load_student_data, format_student_data_for_embedding

class SupabaseVectorStore:
    def __init__(self):
        """Initialize Supabase client with pgvector"""
        self.supabase: Client = create_client(
            config.SUPABASE_URL,
            config.SUPABASE_KEY
        )
        self.embedding_model = get_embedding_model()
        self.table_name = "student_embeddings"
        print(f"✅ Connected to Supabase: {config.SUPABASE_URL[:30]}...")
        
    def create_index(self):
        """
        Generate embeddings for all students in Supabase students table
        and store them in student_embeddings table
        """
        print("📊 Fetching students from Supabase...")
        
        # Get all students from students table
        result = self.supabase.table("students").select("*").execute()
        
        if not result.data:
            print("⚠️  No students found in database!")
            return
        
        students = result.data
        print(f"✅ Found {len(students)} students")
        
        # Clear existing embeddings (optional - remove if you want to keep old data)
        print("🗑️  Clearing old embeddings...")
        self.supabase.table(self.table_name).delete().neq('id', 0).execute()
        
        print("🔄 Generating embeddings...")
        for i, student in enumerate(students):
            print(f"Processing {i+1}/{len(students)}: {student['name']}")
            
            # Format student data for embedding
            content = format_student_data_for_embedding(student)
            
            # Generate embedding
            embedding = self.embedding_model.embed_text(content)
            
            # Prepare data for insertion
            data = {
                "student_id": student["student_id"],
                "student_name": student["name"],
                "content": content,
                "embedding": embedding,
                "metadata": student  # Store full student data as JSON
            }
            
            # Insert into Supabase
            insert_result = self.supabase.table(self.table_name).insert(data).execute()
            
            if not insert_result.data:
                print(f"❌ Failed to insert {student['student_id']}")
            else:
                print(f"✅ Embedded {student['student_id']}")
            
            # Rate limiting - wait 1 second between API calls
            time.sleep(1)
        
        print("✅ Index creation complete!")
    
    def search(self, query: str, k: int = 2) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Search for similar students using pgvector cosine similarity
        """
        # Generate query embedding
        query_embedding = self.embedding_model.embed_text(query)
        
        # Perform similarity search using Supabase RPC function
        result = self.supabase.rpc(
            'match_student_embeddings',
            {
                'query_embedding': query_embedding,
                'match_count': k
            }
        ).execute()
        
        if not result.data:
            print("⚠️  No results found")
            return [], []
        
        # Extract content and metadata
        retrieved_docs = [item['content'] for item in result.data]
        retrieved_metadata = [item['metadata'] for item in result.data]
        
        return retrieved_docs, retrieved_metadata
    
    def get_student_by_id(self, student_id: str) -> Dict[str, Any]:
        """
        Retrieve specific student data by ID
        Always fetches FRESH data from students table (not cached embeddings)
        """
        # Fetch fresh data directly from students table, not from cached embeddings
        result = self.supabase.table("students")\
            .select("*")\
            .eq("student_id", student_id)\
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    
    def get_student_content_by_id(self, student_id: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Retrieve student content and metadata by ID
        Fetches fresh data from students table and formats it
        """
        # Fetch fresh data from students table
        result = self.supabase.table("students")\
            .select("*")\
            .eq("student_id", student_id)\
            .execute()
        
        if result.data and len(result.data) > 0:
            student_data = result.data[0]
            # Format the fresh data for embedding format
            from src.utils import format_student_data_for_embedding
            content = format_student_data_for_embedding(student_data)
            return content, student_data
        return None, None


# Singleton instance
_vector_store = None

def get_vector_store() -> SupabaseVectorStore:
    """Get or create the vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = SupabaseVectorStore()
    return _vector_store