import faiss
import numpy as np
import os
import pickle
import hashlib


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

        # ✅ NEW: dedup tracking (safe, in-memory only)
        self.seen_hashes = set()

        # ✅ Detect if persistence is possible (Render vs Docker safe)
        self.use_persistence = self._can_use_persistence()

        self._init_index()
        self._load_if_exists()

    # =========================
    # NEW: HASH FUNCTION
    # =========================
    def _get_hash(self, text: str):
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    # =========================
    # ENV SAFE PERSISTENCE CHECK
    # =========================
    def _can_use_persistence(self):
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

            # 🔥 rebuild dedup set from existing metadata
            for meta in self.metadata:
                text = meta.get("text", "")
                self.seen_hashes.add(self._get_hash(text))

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
    # ADD VECTORS (FIXED)
    # =========================
    def add(self, embeddings, metadatas):
        if len(embeddings) != len(metadatas):
            raise ValueError("Embeddings and metadata length mismatch")

        filtered_embeddings = []
        filtered_metadatas = []

        for emb, meta in zip(embeddings, metadatas):
            text = meta.get("text", "")
            text_hash = self._get_hash(text)

            # 🔥 SKIP DUPLICATES
            if text_hash in self.seen_hashes:
                continue

            self.seen_hashes.add(text_hash)
            filtered_embeddings.append(emb)
            filtered_metadatas.append(meta)

        if not filtered_embeddings:
            return

        filtered_embeddings = self._normalize(filtered_embeddings)

        self.index.add(filtered_embeddings)
        self.metadata.extend(filtered_metadatas)

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
        self.seen_hashes = set()

        if self.use_persistence:
            if os.path.exists(self.index_path):
                os.remove(self.index_path)

            if os.path.exists(self.meta_path):
                os.remove(self.meta_path)