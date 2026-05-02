import faiss
import numpy as np
import os
import pickle


class FAISSStore:
    """
    Production-ready FAISS store for OpenAI embeddings (text-embedding-3-small).

    - Fixed dimension = 1536
    - Cosine similarity (via normalization)
    - OPTIONAL persistence (Docker safe, Render safe)
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

        # ✅ Detect if persistence is possible (Render vs Docker safe)
        self.use_persistence = self._can_use_persistence()

        self._init_index()
        self._load_if_exists()

    # =========================
    # ENV SAFE PERSISTENCE CHECK
    # =========================
    def _can_use_persistence(self):
        """
        Render Free = no reliable disk → disable persistence safely
        Docker = allowed → enable persistence
        """
        try:
            test_dir = os.path.dirname(self.index_path) or "."
            return os.access(test_dir, os.W_OK)
        except Exception:
            return False

    # =========================
    # INIT INDEX
    # =========================
    def _init_index(self):
        self.index = faiss.IndexFlatIP(self.dimension)

    # =========================
    # LOAD / SAVE
    # =========================
    def _load_if_exists(self):
        if not self.use_persistence:
            return

        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)

            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)

    def _save(self):
        if not self.use_persistence:
            return

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
        if len(embeddings) != len(metadatas):
            raise ValueError("Embeddings and metadata length mismatch")

        embeddings = self._normalize(embeddings)

        self.index.add(embeddings)
        self.metadata.extend(metadatas)

        if self.index.ntotal != len(self.metadata):
            raise RuntimeError("FAISS index and metadata out of sync!")

        self._save()

    # =========================
    # SEARCH
    # =========================
    def search(self, query_embedding, top_k=5, doc_id=None):
        if self.index is None or self.index.ntotal == 0:
            return []

        query_embedding = self._normalize([query_embedding])

        scores, indices = self.index.search(query_embedding, top_k * 3)

        results = []

        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue

            meta = self.metadata[idx]

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

        # only delete if persistence allowed
        if self.use_persistence:
            if os.path.exists(self.index_path):
                os.remove(self.index_path)

            if os.path.exists(self.meta_path):
                os.remove(self.meta_path)