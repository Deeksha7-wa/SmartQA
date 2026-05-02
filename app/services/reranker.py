import re

class RerankerService:
    def __init__(self):
        pass

    def _score(self, query: str, text: str) -> float:
        """
        Improved lightweight reranking (still no ML)
        """

        if not text:
            return 0.0

        query_tokens = set(re.findall(r"\w+", query.lower()))
        text_lower = text.lower()
        text_tokens = set(re.findall(r"\w+", text_lower))

        if not query_tokens:
            return 0.0

        overlap = len(query_tokens & text_tokens)
        coverage = sum(1 for t in query_tokens if t in text_tokens)

        base_score = (overlap + coverage) / (len(query_tokens) + 1e-6)

        # -------------------------
        # 🔥 STRUCTURE BOOST
        # -------------------------
        boost = 0.0

        if any(k in text_lower for k in ["skills", "technical", "backend", "experience"]):
            boost += 0.15

        if any(k in text_lower for k in ["ai", "ml", "machine learning", "deep learning"]):
            boost += 0.10

        if any(k in text_lower for k in ["project", "developed", "built"]):
            boost += 0.05

        # -------------------------
        # 🔥 LENGTH PENALTY (removes noisy chunks)
        # -------------------------
        length_penalty = len(text_tokens) / 6000

        final_score = base_score + boost - length_penalty

        return float(final_score)

    def rerank(self, query: str, chunks: list[dict]):
        """
        Re-rank FAISS results without ML model
        """

        if not chunks:
            return []

        reranked = []

        for chunk in chunks:
            text = chunk.get("metadata", {}).get("text", "")

            score = self._score(query, text)

            reranked.append({
                **chunk,
                "rerank_score": score
            })

        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)

        return reranked