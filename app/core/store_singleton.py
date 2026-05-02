from app.vectorstore.faiss_store import FAISSStore

# Single global FAISS instance (shared across ingestion + retrieval)
GLOBAL_STORE = FAISSStore()