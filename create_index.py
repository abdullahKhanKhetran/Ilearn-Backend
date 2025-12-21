from src.supabase_vector_store import get_vector_store

print("=" * 60)
print("Creating vector embeddings from Supabase students...")
print("=" * 60)

vector_store = get_vector_store()
vector_store.create_index()

print("\n" + "=" * 60)
print("✅ Embeddings created successfully!")
print("=" * 60)