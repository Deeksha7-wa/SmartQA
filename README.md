# Smart Document Q&A System (RAG-Based AI Assistant)

A production-grade Retrieval-Augmented Generation (RAG) system that allows users to upload documents (PDF/DOCX) and ask natural language questions grounded strictly in document content.

Built using FastAPI, FAISS, OpenAI Embeddings, PostgreSQL, SQLAlchemy, Alembic, and Docker.

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
- Semantic search using FAISS vector database
- OpenAI embeddings (`text-embedding-3-small`)
- RAG-based LLM answering (GPT-4o-mini)
- PostgreSQL persistence with structured schema
- Alembic migrations for database versioning
- Fully Dockerized system

---

# 🏗️ System Architecture

User  
→ FastAPI (API Layer)  
→ Document Parser (PDF/DOCX)  
→ Chunking (Overlapping Strategy)  
→ OpenAI Embeddings  
→ FAISS Vector Store  
→ Semantic Retrieval (Top-K chunks)  
→ OpenAI GPT (RAG Prompt)  
→ Final Answer + Sources  
→ PostgreSQL (Storage Layer)

---

# ⚙️ Tech Stack

FastAPI  
FAISS  
OpenAI API  
PostgreSQL  
SQLAlchemy  
Alembic  
Docker + Docker Compose  

---

# 📌 API Endpoints

## 📄 Upload Document

POST /documents/upload

Response:
```json id="upload_res"
{
  "document_id": "...",
  "status": "completed",
  "chunks_indexed": 6
}
