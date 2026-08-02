import os
import shutil
import fitz # PyMuPDF
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.models.user import User
from app.core.config import settings
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
        filepath = os.path.join(settings.UPLOAD_PATH, f"{owner.id}_{safe_filename}")
        
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        doc_record = await self.create_document_record(safe_filename, filepath, file_size, owner.id)
        
        # Extract text in background or synchronously (we'll do sync for simplicity here, but in production, use Celery/BackgroundTasks)
        try:
            text_content = self.extract_text(filepath)
            page_count = self.get_page_count(filepath)
            
            doc_record.page_count = page_count
            
            # Pass to RAG service for chunking and embedding
            from app.services.rag_service import rag_service
            rag_service.process_and_store_document(text_content, doc_record.id, doc_record.filename)
            
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
