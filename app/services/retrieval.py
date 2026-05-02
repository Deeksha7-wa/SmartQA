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

        texts = [chunk.get("text", "") for chunk in chunks]
        embeddings = self.embedding_service.embed_batch(texts)

        self.vectorstore.add(
            embeddings=embeddings,
            metadatas=chunks
        )

    def retrieve(self, query: str, top_k: int = 5):
        """
        1. FAISS retrieval (expanded pool)
        2. Filtering noise
        3. Reranking
        4. Deduplication (CRITICAL FIX)
        """

        if not query or not query.strip():
            return []

        query_embedding = self.embedding_service.embed(query)

        # 🔥 bigger pool for better recall
        candidate_pool = min(top_k * 6, 30)

        raw_results = self.vectorstore.search(
            query_embedding=query_embedding,
            top_k=candidate_pool
        )

        if not raw_results:
            return []

        # 🔥 FILTER BAD / EMPTY TEXT
        filtered = [
            r for r in raw_results
            if len(r.get("metadata", {}).get("text", "").strip()) > 20
        ]

        if not filtered:
            return []

        reranked_results = self.reranker.rerank(
            query=query,
            chunks=filtered
        )

        # 🔥 DEDUPLICATION (FIX FOR REPEATED CV SECTIONS)
        seen = set()
        unique_results = []

        for r in reranked_results:
            text = r.get("metadata", {}).get("text", "")

            # normalize signature for duplicates
            norm = " ".join(text.lower().split()[:35])

            if norm in seen:
                continue

            seen.add(norm)
            unique_results.append(r)

            if len(unique_results) == top_k:
                break

        return unique_results