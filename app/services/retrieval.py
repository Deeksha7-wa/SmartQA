from app.services.embedding import EmbeddingService
from app.core.store_singleton import GLOBAL_STORE
from app.services.reranker import RerankerService


class RetrievalService:
    def __init__(self):
        # 🔥 Embeddings
        self.embedding_service = EmbeddingService()

        # 🔥 FAISS store
        self.vectorstore = GLOBAL_STORE

        # 🧠 Reranker (NEW)
        self.reranker = RerankerService()

    def index_chunks(self, chunks: list[dict]):
        """
        Convert chunks → embeddings → store in FAISS
        """

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
        1. FAISS retrieval (fast)
        2. Reranking (smart ordering)
        """

        if not query or not query.strip():
            return []

        # 🔍 Step 1: FAISS search (get more candidates first)
        query_embedding = self.embedding_service.embed(query)

        raw_results = self.vectorstore.search(
            query_embedding=query_embedding,
            top_k=top_k * 3   # 🔥 important: expand pool for reranker
        )

        if not raw_results:
            return []

        # 🧠 Step 2: Rerank using cross-encoder
        reranked_results = self.reranker.rerank(
            query=query,
            chunks=raw_results
        )

        # ✂️ Step 3: Return top_k only
        return reranked_results[:top_k]