from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class MessageBase(BaseModel):
    role: str = Field(..., description="user or assistant")
    content: str
    sources: Optional[str] = None

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: str
    created_at: datetime
    
    model_config = {"from_attributes": True}

class ChatBase(BaseModel):
    title: str = "New Chat"

class ChatCreate(ChatBase):
    pass

class ChatUpdate(BaseModel):
    title: Optional[str] = None
    is_pinned: Optional[bool] = None

class ChatResponse(ChatBase):
    id: str
    is_pinned: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

class ChatDetailResponse(ChatResponse):
    messages: List[MessageResponse] = []

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None
