from app.services.ingestion import IngestionService

ingestion = IngestionService()

result = ingestion.process_document(
    file_path="data/sample_docs/sample.txt",
    file_type="txt"
)

print(result)