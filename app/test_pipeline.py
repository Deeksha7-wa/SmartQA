from app.services.ingestion import IngestionService
from app.services.retrieval import RetrievalService
from app.core.store_singleton import GLOBAL_STORE

# Step 1: ingest
ingestion = IngestionService()

ingestion.process_document(
    file_path="data/sample_docs/sample.txt",
    file_type="txt"
)

# Debug
print("FAISS vectors:", GLOBAL_STORE.index.ntotal)
print("Metadata:", len(GLOBAL_STORE.metadata))

# Step 2: retrieve
retrieval = RetrievalService()

results = retrieval.retrieve(
    "What is the refund policy?",
    top_k=3
)

print(results)