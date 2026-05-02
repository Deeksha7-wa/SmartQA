from fastapi import APIRouter, UploadFile, File
import uuid
import os

from app.services.ingestion import IngestionService

router = APIRouter()

# Initialize once
ingestion_service = IngestionService()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload + immediately process document into FAISS
    (Synchronous mode so FastAPI and retrieval share same memory store)
    """

    # Ensure uploads directory exists
    os.makedirs("uploads", exist_ok=True)

    # Save uploaded file
    file_id = str(uuid.uuid4())
    file_path = f"uploads/{file_id}_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract file extension
    file_type = file.filename.split(".")[-1].lower()

    # 🔥 DIRECT INGESTION
    result = ingestion_service.process_document(
        file_path=file_path,
        file_type=file_type,
        filename=file.filename
    )

    # ✅ IMPORTANT FIX: return DB-generated document_id (NOT API uuid)
    return {
        "document_id": result["document_id"],
        "filename": file.filename,
        "status": "completed",
        "chunks_indexed": result["total_chunks"]
    }