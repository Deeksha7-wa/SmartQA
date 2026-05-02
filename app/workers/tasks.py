import os

from app.workers.celery_worker import celery
from app.services.ingestion import IngestionService

ingestion_service = IngestionService()


@celery.task
def process_document_task(file_path: str, file_type: str):

    try:
        result = ingestion_service.process_document(file_path, file_type)

        return {
            "status": "completed",
            "chunks": result["total_chunks"]
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }