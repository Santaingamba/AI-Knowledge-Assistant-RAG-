from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.sqlmodel_models import Document, User
from app.core.config import settings
from app.utils.storage import get_storage
from app.core.exceptions import BadRequestException
from app.utils.logger import setup_logger

logger = setup_logger("document_service")

class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document_record(self, filename: str, filepath: str, file_size: int, owner_id: str) -> Document:
        doc = Document(
            filename=filename,
            filepath=filepath,
            file_size=file_size,
            owner_id=owner_id
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc
        
    async def process_pdf(self, file: UploadFile, owner: User):
        if not file.filename.lower().endswith(".pdf"):
            raise BadRequestException("Only PDF files are allowed.")
            
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > 25 * 1024 * 1024:
            raise BadRequestException("File size exceeds 25 MB limit.")

        safe_filename = file.filename.replace(" ", "_")
        # Use storage abstraction to save the file; the identifier will be the stored path or S3 key
        storage = get_storage()
        stored_path = storage.save_file(f"{owner.id}_{safe_filename}", file.file)

        doc_record = await self.create_document_record(safe_filename, stored_path, file_size, owner.id)
        
        # Extract text in background or synchronously (we'll do sync for simplicity here, but in production, use Celery/BackgroundTasks)
        try:
            text_content = self.extract_text(stored_path)
            page_count = self.get_page_count(stored_path)

            doc_record.page_count = page_count

            # Pass to RAG service for chunking and embedding, include owner_id for isolation
            from app.services.rag_service import rag_service
            rag_service.process_and_store_document(text_content, doc_record.id, doc_record.filename, owner.id)

            doc_record.status = "ready"
        except Exception as e:
            logger.error(f"Error processing document {doc_record.id}: {e}")
            doc_record.status = "error"
            doc_record.error_message = str(e)
            
        await self.db.commit()
        return doc_record

    def extract_text(self, filepath: str) -> str:
        text = ""
        try:
            with fitz.open(filepath) as doc:
                for page in doc:
                    text += page.get_text() + "\n"
        except Exception as e:
            logger.error(f"Failed to extract text from {filepath}: {e}")
            raise ValueError("Corrupted or encrypted PDF.")
        return text
        
    def get_page_count(self, filepath: str) -> int:
        try:
            with fitz.open(filepath) as doc:
                return len(doc)
        except Exception:
            return 0
