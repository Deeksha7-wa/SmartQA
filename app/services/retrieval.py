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

    def _section_boost(self, text: str, query: str) -> int:
        """
        Boost correct CV section based on query intent
        """
        text = text.lower()
        query = query.lower()

        if "employment" in query or "experience" in query:
            return 3 if "work experience" in text or "experience" in text else 0

        if "education" in query:
            return 3 if "education" in text else 0

        if "skill" in query:
            return 3 if "skill" in text else 0

        return 1

    def retrieve(self, query: str, top_k: int = 5):
        if not query or not query.strip():
            return []

        query_embedding = self.embedding_service.embed(query)

        candidate_pool = min(top_k * 6, 30)

        raw_results = self.vectorstore.search(
            query_embedding=query_embedding,
            top_k=candidate_pool
        )

        if not raw_results:
            return []

        # 🔥 FILTER NOISE
        filtered = [
            r for r in raw_results
            if len(r.get("metadata", {}).get("text", "").strip()) > 20
        ]

        if not filtered:
            return []

        # 🧠 RERANK
        reranked_results = self.reranker.rerank(
            query=query,
            chunks=filtered
        )

        # 🔥 FINAL IMPROVEMENT: SECTION-AWARE SORTING
        reranked_results.sort(
            key=lambda r: (
                self._section_boost(
                    r.get("metadata", {}).get("text", ""),
                    query
                ),
                r.get("rerank_score", 0)
            ),
            reverse=True
        )

        # 🔥 DEDUP (KEEP SAME)
        seen = set()
        unique_results = []

        for r in reranked_results:
            text = r.get("metadata", {}).get("text", "")
            norm = " ".join(text.lower().split()[:35])

            if norm in seen:
                continue

            seen.add(norm)
            unique_results.append(r)

            if len(unique_results) == top_k:
                break

        return unique_results