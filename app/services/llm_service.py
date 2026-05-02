# app/services/llm_service.py

from openai import OpenAI
from app.core.config import settings


def build_prompt(context_chunks, question, chat_history=None):
    """
    Builds a strict RAG prompt that enforces:
    - extraction only
    - structure preservation
    - no mixing of document sections
    """

    if not context_chunks:
        context_text = "No relevant context retrieved from the document."
    else:
        context_text = "\n\n".join(
            [
                f"[Chunk {i + 1} | ID: {chunk['metadata'].get('chunk_id', 'unknown')}]\n"
                f"{chunk['metadata'].get('text', '')}"
                for i, chunk in enumerate(context_chunks)
            ]
        )

    history_text = ""
    if chat_history:
        history_text = "\n".join(chat_history[-5:])

    prompt = f"""
You are a STRICT DOCUMENT EXTRACTION ENGINE.

────────────────────────────────────────
CORE RULES
────────────────────────────────────────
- Use ONLY the provided CONTEXT.
- If answer is not found, say EXACTLY:
  "I could not find this information in the document."
- NEVER use external knowledge.
- NEVER hallucinate or infer missing data.

────────────────────────────────────────
STRICT EXTRACTION MODE (CRITICAL)
────────────────────────────────────────
- Return text EXACTLY as present in CONTEXT.
- DO NOT summarize, rewrite, clean, or improve text.
- DO NOT merge multiple chunks unless they are identical sections.
- KEEP duplicates if they appear.
- PRESERVE bullet points, spacing, and ordering.

────────────────────────────────────────
CV / DOCUMENT STRUCTURE RULE (IMPORTANT)
────────────────────────────────────────
- Do NOT mix different sections.
- If question is about:
    • Employment → ONLY use WORK EXPERIENCE / EXPERIENCE sections
    • Education → ONLY use EDUCATION sections
    • Skills → ONLY use SKILLS sections
- Ignore unrelated sections completely.

────────────────────────────────────────
OUTPUT RULES
────────────────────────────────────────
- Never cut answers mid-section or mid-list.
- Always complete full section before responding.
- Maintain original formatting from context.

────────────────────────────────────────

CONTEXT:
{context_text}

CHAT HISTORY:
{history_text}

QUESTION:
{question}

FINAL ANSWER:
"""

    return prompt.strip()


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_answer(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a strict document extraction engine. "
                            "You must follow section boundaries and never mix content. "
                            "Return only exact text from context."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=3000
            )

            return response.choices[0].message.content.strip()

        except Exception:
            return "LLM service temporarily unavailable."