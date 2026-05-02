import faiss
import numpy as np
import os
import pickle


class FAISSStore:
    """
    Production-ready FAISS store for OpenAI embeddings (text-embedding-3-small).
    - Fixed dimension = 1536
    - Cosine similarity (via normalization)
    - Persistent index + metadata
    - Safe retrieval with doc filtering
    """

    OPENAI_EMBEDDING_DIM = 1536

    def __init__(
            self,
            index_path: str = "faiss.index",
            meta_path: str = "faiss_meta.pkl"
    ):
        self.dimension = self.OPENAI_EMBEDDING_DIM
        self.index = None
        self.metadata = []

        self.index_path = index_path
        self.meta_path = meta_path

        self._load_if_exists()

    # =========================
    # INIT INDEX
    # =========================
    def _init_index(self):
        # Inner product + normalization = cosine similarity
        self.index = faiss.IndexFlatIP(self.dimension)

    # =========================
    # LOAD / SAVE
    # =========================
    def _load_if_exists(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)

            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)

    def _save(self):
        faiss.write_index(self.index, self.index_path)

        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    # =========================
    # NORMALIZATION
    # =========================
    def _normalize(self, vectors):
        vectors = np.asarray(vectors, dtype="float32")

        if vectors.ndim != 2:
            raise ValueError("Embeddings must be 2D array (n, d)")

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension mismatch: got {vectors.shape[1]}, expected {self.dimension}"
            )

        faiss.normalize_L2(vectors)
        return vectors

    # =========================
    # ADD VECTORS
    # =========================
    def add(self, embeddings, metadatas):
        """
        embeddings: list[list[float]]
        metadatas: list[dict]
        """

        if len(embeddings) != len(metadatas):
            raise ValueError("Embeddings and metadata length mismatch")

        embeddings = self._normalize(embeddings)

        if self.index is None:
            self._init_index()

        self.index.add(embeddings)
        self.metadata.extend(metadatas)

        if self.index.ntotal != len(self.metadata):
            raise RuntimeError("FAISS index and metadata out of sync!")

        self._save()

    # =========================
    # SEARCH
    # =========================
    def search(self, query_embedding, top_k=5, doc_id=None):
        """
        Returns:
        [
            {
                "metadata": {...},
                "score": float
            }
        ]
        """

        if self.index is None or self.index.ntotal == 0:
            return []

        query_embedding = self._normalize([query_embedding])

        scores, indices = self.index.search(query_embedding, top_k * 3)

        results = []

        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue

            meta = self.metadata[idx]

            # optional document filtering
            if doc_id and meta.get("document_id") != doc_id:
                continue

            results.append({
                "metadata": meta,
                "score": float(round(scores[0][i], 4))
            })

            if len(results) == top_k:
                break

        return results

    # =========================
    # RESET STORE
    # =========================
    def reset(self):
        self.index = None
        self.metadata = []

        if os.path.exists(self.index_path):
            os.remove(self.index_path)

        if os.path.exists(self.meta_path):
            os.remove(self.meta_path)