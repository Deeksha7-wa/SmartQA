from app.services.retrieval import RetrievalService

retrieval = RetrievalService()

results = retrieval.retrieve("What is the refund policy?", top_k=3)
from app.core.store_singleton import GLOBAL_STORE

print("FAISS vectors:", GLOBAL_STORE.index.ntotal)
print("Metadata:", len(GLOBAL_STORE.metadata))

print(results)