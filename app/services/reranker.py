import re


class RerankerService:
    def __init__(self):
        pass

    def _detect_intent(self, query: str):
        q = query.lower()

        if any(k in q for k in ["employment", "experience", "job", "work"]):
            return "experience"

        if any(k in q for k in ["education", "study", "degree"]):
            return "education"

        if any(k in q for k in ["skill", "technology", "tech"]):
            return "skills"

        return "general"

    def _score(self, query: str, text: str) -> float:
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

        intent = self._detect_intent(query)

        # -------------------------
        # 🔥 STRONG SECTION PRIORITY BOOST
        # -------------------------
        boost = 0.0

        if intent == "experience":
            if "work experience" in text_lower or "experience" in text_lower:
                boost += 0.5
            if "education" in text_lower:
                boost -= 0.3  # HARD PENALTY

        if intent == "education":
            if "education" in text_lower:
                boost += 0.5
            if "experience" in text_lower:
                boost -= 0.2

        if intent == "skills":
            if "skills" in text_lower:
                boost += 0.4

        # -------------------------
        # LIGHT SIGNAL BOOSTS
        # -------------------------
        if any(k in text_lower for k in ["developed", "built", "implemented"]):
            boost += 0.05

        # -------------------------
        # LENGTH PENALTY (better tuned)
        # -------------------------
        length_penalty = min(len(text_tokens) / 8000, 0.2)

        final_score = base_score + boost - length_penalty

        return float(final_score)

    def rerank(self, query: str, chunks: list[dict]):
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