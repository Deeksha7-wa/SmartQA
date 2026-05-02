from app.services.chunking import chunk_text
from app.services.file_parser import extract_text
from app.services.embedding import EmbeddingService
from app.core.store_singleton import GLOBAL_STORE

from app.db.session import SessionLocal
from app.db.models import Document, Chunk

import uuid
from datetime import datetime


class IngestionService:

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def process_document(self, file_path: str, file_type: str, filename: str):

        db = SessionLocal()
        document_id = None

        try:
            # 🧠 STEP 1
            raw_text = extract_text(file_path, file_type)

            # 🧠 STEP 2
            chunks = chunk_text(raw_text)

            # 🧠 STEP 3 - Save document
            document_id = str(uuid.uuid4())

            document = Document(
                document_id=document_id,
                filename=filename,
                status="processing",
                upload_time=datetime.utcnow()
            )

            db.add(document)
            db.commit()

            processed_chunks = []

            # 🧠 STEP 4 - Save chunks
            for i, chunk in enumerate(chunks):

                chunk_id = str(uuid.uuid4())

                db_chunk = Chunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    text=chunk,
                    chunk_index=i,
                    faiss_id=None
                )

                db.add(db_chunk)

                processed_chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk,
                    "index": i,
                    "document_id": document_id
                })

            # 🔥 IMPORTANT: ensure DB flush before commit
            db.flush()
            db.commit()

            # 🧠 STEP 5 - embeddings
            texts = [c["text"] for c in processed_chunks]
            embeddings = self.embedding_service.embed_batch(texts)

            GLOBAL_STORE.add(
                embeddings=embeddings,
                metadatas=processed_chunks
            )

            # 🟢 STEP 6 - update status
            db.query(Document).filter(
                Document.document_id == document_id
            ).update({"status": "completed"})

            db.commit()

            return {
                "document_id": document_id,
                "total_chunks": len(processed_chunks),
                "status": "completed"
            }

        except Exception as e:
            db.rollback()

            if document_id:
                db.query(Document).filter(
                    Document.document_id == document_id
                ).update({"status": "failed"})
                db.commit()

            print("❌ INGESTION ERROR:", str(e))
            raise e

        finally:
            db.close()
