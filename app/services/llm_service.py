# app/services/llm_service.py

from openai import OpenAI
from app.core.config import settings


def build_prompt(context_chunks, question, chat_history=None):
    """
    Builds a strict RAG prompt that minimizes hallucination
    and forces answers only from retrieved document chunks.
    """

    # Handle empty retrieval safely
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

    # Keep only recent chat turns for context continuity
    history_text = ""
    if chat_history:
        history_text = "\n".join(chat_history[-5:])

    prompt = f"""
You are a strict document-based question answering system.

RULES:
- Answer ONLY using the provided CONTEXT.
- If the answer is not clearly available in the CONTEXT, respond exactly:
  "I could not find this information in the document."
- Do NOT use outside knowledge.
- Do NOT hallucinate.
- Provide a COMPLETE and DETAILED answer using all relevant information from the context.
- Do NOT summarize unless explicitly asked.
- Do NOT shorten lists, bullet points, or structured data.
- If the answer contains skills, experience, or any list, return ALL items exactly as present.
- Preserve formatting from the context whenever possible.
- If chat history is irrelevant, ignore it.

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
    """
    Handles all LLM interactions for SmartQA.
    Uses OpenAI GPT for strict document-grounded answers.
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_answer(self, prompt: str) -> str:
        """
        Sends prompt to OpenAI and returns grounded answer.
        Includes fallback protection.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise document QA assistant. "
                            "Answer strictly from provided context only. "
                            "Do not summarize or shorten structured information."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.2,
                max_tokens=1800
            )

            return response.choices[0].message.content.strip()

        except Exception:
            return "LLM service temporarily unavailable. Please try again later."