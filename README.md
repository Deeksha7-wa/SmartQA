# Smart Document Q&A System (RAG-Based AI Assistant)

A production-grade Retrieval-Augmented Generation (RAG) system that allows users to upload documents (PDF/DOCX) and ask natural language questions grounded strictly in document content.

Built using FastAPI, FAISS, OpenAI Embeddings, PostgreSQL, SQLAlchemy, Alembic, Celery, and Docker.

---

# 🌐 Live Deployment

Hosted API (Swagger UI):
https://smartqa-bnv4.onrender.com/docs

Local Development:
http://127.0.0.1:8000/docs

---

# 🚀 Features

- Upload PDF / DOCX documents
- Intelligent chunking with overlap strategy
- Semantic search using FAISS vector database
- OpenAI embeddings (text-embedding-3-small)
- RAG-based LLM answering (GPT-4o-mini)
- Lightweight reranking layer for improved retrieval accuracy
- PostgreSQL persistence with structured schema
- Alembic migrations for database versioning
- Fully Dockerized system
- Async processing using Celery + Redis

---

# 🏗️ System Architecture

User  
→ FastAPI (API Layer)  
→ Celery Queue (Redis)  
→ Document Parser (PDF/DOCX)  
→ Chunking (Overlapping Strategy)  
→ OpenAI Embeddings  
→ FAISS Vector Store  
→ Reranking Layer (lexical scoring)  
→ Semantic Retrieval (Top-K chunks)  
→ OpenAI GPT (RAG Prompt)  
→ Final Answer + Sources  
→ PostgreSQL (Storage Layer)

---

# ⚙️ Tech Stack

FastAPI  
Celery  
Redis  
FAISS  
PostgreSQL  
SQLAlchemy  
Alembic  
OpenAI API  
Docker + Docker Compose  

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

This starts:
- FastAPI backend
- Celery worker (async processing)
- Redis (message broker)
- PostgreSQL database (smartqa)
- FAISS vector system

---

# ⚡ Celery Worker

Celery is used for background document processing to avoid blocking API requests.

Run worker:

celery -A app.workers.celery_worker.celery worker --pool=solo --loglevel=info

---

# 🗄️ PostgreSQL Database (smartqa)

Access database:

docker exec -it smartqa_postgres psql -U postgres -d smartqa

---

Tables:
- documents
- chunks
- chat_logs
- alembic_version

---

# 🧪 Alembic Migrations

Run migrations:

docker-compose run api alembic upgrade head

Create migration:

docker-compose run api alembic revision --autogenerate -m "init"

---

# 🧠 Key Design Decisions

## 1. Chunking Strategy
- 800-character chunks
- 150-character overlap
- improves semantic retrieval accuracy

---

## 2. Embeddings

OpenAI model:
text-embedding-3-small

Why:
- high semantic accuracy
- fast inference
- production-grade performance
- batch embedding support

---

## 3. FAISS Vector Search

- fast similarity search
- top-k retrieval (k=5)
- stores embeddings + metadata

---

## 4. Reranking Layer

A lightweight lexical reranking system is applied after FAISS retrieval to improve relevance before passing context to the LLM.

This improves:
- retrieval precision
- contextual ranking
- final answer accuracy

---

## 5. RAG Pipeline

- strict context-only answering
- no hallucination allowed
- fallback when answer not found

---

## 6. PostgreSQL Layer

Used for:
- document tracking
- chunk storage
- chat history logs
- schema versioning (Alembic)

---

## 7. Docker Architecture

- FastAPI backend
- Celery worker
- Redis queue
- PostgreSQL (smartqa)
- FAISS index system

---

# 📈 Scalability

- FAISS → Pinecone / Weaviate upgrade possible
- PostgreSQL → production-grade persistence
- Celery → horizontally scalable workers
- Stateless API → cloud deployment ready

---

# 🔮 Future Improvements

- Streaming responses (token streaming UX)
- Multi-document Q&A
- User authentication system
- React frontend UI
- Citation highlighting in responses

---

# 🧑‍💻 System Highlights

✔ Full RAG pipeline  
✔ FAISS semantic search  
✔ OpenAI embeddings integration  
✔ Celery async processing  
✔ PostgreSQL + Alembic migrations  
✔ Lightweight reranking layer  
✔ Dockerized production setup  
✔ Real-world scalable architecture  

---

# 🚀 One Command Run

docker-compose up --build
