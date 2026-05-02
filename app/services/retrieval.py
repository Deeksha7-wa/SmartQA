from app.services.embedding import EmbeddingService
from app.core.store_singleton import GLOBAL_STORE
from app.services.reranker import RerankerService


class RetrievalService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vectorstore = GLOBAL_STORE
        self.reranker = RerankerService()

    def index_chunks(self, chunks: list[dict]):
        if not chunks:
            return

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_service.embed_batch(texts)

        self.vectorstore.add(
            embeddings=embeddings,
            metadatas=chunks
        )

    def retrieve(self, query: str, top_k: int = 5):
        """
        1. FAISS retrieval (bigger candidate pool)
        2. Reranking (final ordering)
        """

        if not query or not query.strip():
            return []

        query_embedding = self.embedding_service.embed(query)

        # 🔥 IMPROVED: larger pool for better reranking
        candidate_pool = min(top_k * 5, 25)

        raw_results = self.vectorstore.search(
            query_embedding=query_embedding,
            top_k=candidate_pool
        )

        if not raw_results:
            return []

        # 🔥 FILTER LOW QUALITY CHUNKS
        filtered = [
            r for r in raw_results
            if len(r.get("metadata", {}).get("text", "")) > 20
        ]

        if not filtered:
            return []

        reranked_results = self.reranker.rerank(
            query=query,
            chunks=filtered
        )

        return reranked_results[:top_k]