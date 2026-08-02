from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentBase(BaseModel):
    filename: str

class DocumentCreate(DocumentBase):
    filepath: str
    file_size: int

class DocumentUpdate(BaseModel):
    filename: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    page_count: Optional[int] = None

class DocumentResponse(DocumentBase):
    id: str
    file_size: int
    page_count: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}
