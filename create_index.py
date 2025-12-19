from src.vector_store import get_vector_store

print("Creating vector store index from student data...")
vector_store = get_vector_store()
print("✓ Index created and loaded successfully!")
print(f"Total documents in index: {len(vector_store.documents)}")

# Show what students are indexed
from src.utils import load_student_data
students = load_student_data()
print("\nIndexed students:")
for s in students:
    print(f"  - {s['student_id']}: {s['name']}")