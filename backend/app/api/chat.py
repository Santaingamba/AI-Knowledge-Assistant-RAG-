import json
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List
from app.core.database import get_db
from app.models import User, Chat, Message
from app.schemas.chat import ChatResponse, ChatDetailResponse, ChatRequest, MessageResponse
from app.services import get_current_user
from app.services import rag_service
from app.core.exceptions import NotFoundException

router = APIRouter()

@router.post("/", response_model=ChatDetailResponse)
async def ask_question(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    chat_id = request.chat_id
    
    if chat_id:
        # Verify chat exists and belongs to user
        result = await db.execute(select(Chat).where(Chat.id == chat_id, Chat.owner_id == current_user.id))
        chat = result.scalars().first()
        if not chat:
            raise NotFoundException("Chat not found")
    else:
        # Create new chat
        chat = Chat(title=request.message[:50] + "...", owner_id=current_user.id)
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        
    # Save user message
    user_msg = Message(chat_id=chat.id, role="user", content=request.message)
    db.add(user_msg)
    
    # Query RAG — pass current_user.id for per-tenant isolation
    answer, sources = rag_service.query_documents(request.message, current_user.id)
    
    # Save assistant message
    assistant_msg = Message(
        chat_id=chat.id, 
        role="assistant", 
        content=answer, 
        sources=json.dumps(sources) if sources else None
    )
    db.add(assistant_msg)
    
    await db.commit()
    
    # Refresh to return full chat details
    result = await db.execute(select(Chat).where(Chat.id == chat.id))
    chat_full = result.scalars().first()
    
    return chat_full

@router.get("/history", response_model=List[ChatResponse])
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Chat).where(Chat.owner_id == current_user.id).order_by(Chat.updated_at.desc()))
    return result.scalars().all()

@router.get("/{chat_id}", response_model=ChatDetailResponse)
async def get_chat_details(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Chat).where(Chat.id == chat_id, Chat.owner_id == current_user.id))
    chat = result.scalars().first()
    if not chat:
        raise NotFoundException("Chat not found")
    return chat

@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Chat).where(Chat.id == chat_id, Chat.owner_id == current_user.id))
    chat = result.scalars().first()
    if not chat:
        raise NotFoundException("Chat not found")
        
    await db.delete(chat)
    await db.commit()
    return None
