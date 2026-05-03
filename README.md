# Smart Document Q&A System (RAG-Based AI Assistant)

A production-style Retrieval-Augmented Generation (RAG) system that allows users to upload documents (PDF/DOCX) and ask natural language questions grounded strictly in document content.

Built using FastAPI, FAISS, OpenAI Embeddings, Celery, Redis, PostgreSQL, SQLAlchemy, Alembic, and Docker.

---

# 🌐 Live Deployment

**Hosted API (Swagger UI):**  
https://smartqa-bnv4.onrender.com/docs

**Local Development:**  
http://127.0.0.1:8000/docs

---

# 🚀 Features

- Upload PDF / DOCX documents
- Intelligent chunking with overlap strategy
- Semantic search using FAISS
- OpenAI embeddings (`text-embedding-3-small`)
- RAG-based LLM answering (GPT-4o-mini)
- Async processing using Celery + Redis
- PostgreSQL persistence (`smartqa` database)
- Alembic migrations support
- Fully Dockerized system

---

# 🏗️ System Architecture

User  
→ FastAPI (API Layer)  
→ Celery Queue (Redis)  
→ Background Worker  
→ Document Parsing (PDF/DOCX)  
→ Chunking (Overlapping Strategy)  
→ OpenAI Embeddings  
→ FAISS Vector Store  
→ Semantic Retrieval  
→ OpenAI GPT (RAG Prompt)  
→ Final Answer + Sources  

---

# ⚙️ Tech Stack

FastAPI  
Celery  
Redis  
FAISS  
PostgreSQL  
SQLAlchemy + Alembic  
OpenAI API  
Docker + Docker Compose  

---

# 🧠 Celery Worker Code

import os  
from celery import Celery  

REDIS_URL = os.environ["REDIS_URL"]

celery = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    imports=("app.workers.tasks",)
)

---

# 📌 API Endpoints

## Upload Document

POST /documents/upload

Response:
{
  "document_id": "...",
  "status": "completed",
  "chunks_indexed": 6
}

---

## Ask Question

POST /chat/ask

Request:
{
  "question": "give employment details",
  "doc_id": "..."
}

Response:
{
  "answer": "...",
  "retrieved_chunks": 5
}

---

## Health Check

GET /

Response:
{
  "status": "running"
}

---

# 🐳 Docker Setup

Run full system:

docker-compose up --build

---

# PostgreSQL (Database: smartqa)

services:
  postgres:
    image: postgres:15
    container_name: smartqa_db
    environment:
      POSTGRES_DB: smartqa
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"

---

# ⚡ Celery Worker Run

docker-compose run worker celery -A app.workers.celery_worker.celery worker --loglevel=info

OR

docker-compose up worker

---

# 🧠 Key Design Decisions

Chunking: 800 characters with overlap  
Embeddings: OpenAI text-embedding-3-small  
Search: FAISS vector similarity search  
RAG: Strict context-only prompting  
Async: Celery + Redis background processing  
DB: PostgreSQL with Alembic migrations  

---

# 📈 Scalability

FAISS → can be replaced with Pinecone / Weaviate  
Celery → horizontally scalable workers  
PostgreSQL → production-ready persistence  
Stateless API → cloud deployment ready  

---

# 🔮 Future Improvements

Streaming responses  
Reranker model  
Multi-document Q&A  
User authentication  
React frontend  
Citation highlighting  

---

# 🧑‍💻 System Highlights

✔ Full RAG pipeline  
✔ FAISS semantic search  
✔ OpenAI embeddings integration  
✔ Async Celery architecture  
✔ PostgreSQL persistence  
✔ Alembic migrations  
✔ Dockerized system  
✔ Cloud deployment ready  

---

# 🚀 One Command Run

docker-compose up --build

---

# 📬 Links

GitHub Repo: https://github.com/your-username/smart-doc-qa  
Live API: https://smartqa-bnv4.onrender.com/docs
