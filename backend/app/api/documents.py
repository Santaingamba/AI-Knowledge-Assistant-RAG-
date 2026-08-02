from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.services.auth_service import get_current_user
from app.services.document_service import DocumentService
from app.core.exceptions import NotFoundException
import os

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    doc_service = DocumentService(db)
    doc = await doc_service.process_pdf(file, current_user)
    return doc

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).where(Document.owner_id == current_user.id).order_by(Document.created_at.desc()))
    return result.scalars().all()

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).where(Document.id == document_id, Document.owner_id == current_user.id))
    doc = result.scalars().first()
    
    if not doc:
        raise NotFoundException("Document not found")
        
    # Remove file from disk
    if os.path.exists(doc.filepath):
        os.remove(doc.filepath)
        
    # In a full production app, you would also delete from ChromaDB here.
    
    await db.delete(doc)
    await db.commit()
    return None
