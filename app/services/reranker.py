import re
class RerankerService:
    def __init__(self):
        # No ML model (fully lightweight)
        pass

    def _score(self, query: str, text: str) -> float:
        """
        Lightweight lexical similarity scoring
        """

        if not text:
            return 0.0

        query_tokens = set(re.findall(r"\w+", query.lower()))
        text_tokens = set(re.findall(r"\w+", text.lower()))

        if not query_tokens:
            return 0.0

        overlap = len(query_tokens & text_tokens)
        coverage = sum(1 for t in query_tokens if t in text_tokens)

        return float((overlap + coverage) / (len(query_tokens) + 1e-6))

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