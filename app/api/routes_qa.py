from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

from app.services.retrieval import RetrievalService
from app.services.llm_service import LLMService, build_prompt

# 🔥 DB IMPORTS (NEW)
from app.db.session import SessionLocal
from app.db.models import ChatLog

router = APIRouter()

retrieval_service = RetrievalService()
llm_service = LLMService()


class AskRequest(BaseModel):
    question: str
    doc_id: str


@router.post("/ask")
def ask_question(payload: AskRequest):

    db = SessionLocal()

    # 🔍 Step 1
    retrieved_chunks = retrieval_service.retrieve(
        query=payload.question,
        top_k=5
    )

    if not retrieved_chunks:
        answer = "I could not find this information in the document."

        # 💾 SAVE EVEN FAILED CHAT
        chat = ChatLog(
            document_id=payload.doc_id,
            question=payload.question,
            answer=answer,
            timestamp=datetime.utcnow()
        )

        db.add(chat)
        db.commit()
        db.close()

        return {
            "question": payload.question,
            "doc_id": payload.doc_id,
            "retrieved_chunks": 0,
            "answer": answer,
            "answer_source": None,
            "supporting_sources": []
        }

    # 🧠 Step 2
    prompt = build_prompt(
        context_chunks=retrieved_chunks,
        question=payload.question
    )

    # 🤖 Step 3
    answer = llm_service.generate_answer(prompt)

    # 📌 Step 4 sources
    sources = []

    for chunk in retrieved_chunks:
        metadata = chunk.get("metadata", {})

        sources.append({
            "chunk_id": metadata.get("chunk_id", "unknown"),
            "faiss_score": chunk.get("score", 0.0),
            "rerank_score": chunk.get("rerank_score", 0.0),
            "preview": metadata.get("text", "")[:300]
        })

    answer_source = max(
        sources,
        key=lambda x: x.get("rerank_score", 0.0)
    ) if sources else None

    supporting_sources = [
        s for s in sources
        if answer_source and s["chunk_id"] != answer_source["chunk_id"]
    ]

    # 💾 STEP 7 — SAVE CHAT LOG (🔥 MAIN FIX)
    chat = ChatLog(
        document_id=payload.doc_id,
        question=payload.question,
        answer=answer,
        timestamp=datetime.utcnow()
    )

    db.add(chat)
    db.commit()
    db.close()

    # 📤 response
    return {
        "question": payload.question,
        "doc_id": payload.doc_id,
        "retrieved_chunks": len(retrieved_chunks),
        "answer": answer,
        "answer_source": answer_source,
        "supporting_sources": supporting_sources
    }