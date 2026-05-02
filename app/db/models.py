from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime
from datetime import datetime
from app.db.session import Base   # ✅ IMPORTANT FIX

# 📄 DOCUMENT TABLE
class Document(Base):
    __tablename__ = "documents"

    document_id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="processing")
    upload_time = Column(DateTime, default=datetime.utcnow)


# 🧩 CHUNK TABLE
class Chunk(Base):
    __tablename__ = "chunks"

    chunk_id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.document_id"), index=True)
    text = Column(Text, nullable=False)
    chunk_index = Column(Integer)
    faiss_id = Column(Integer, nullable=True)


# 💬 CHAT LOG
class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("documents.document_id"))
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)