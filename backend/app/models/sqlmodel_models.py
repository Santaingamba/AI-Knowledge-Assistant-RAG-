from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import datetime
from typing import List, Optional

class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    email: str = Field(index=True, nullable=False, unique=True)
    hashed_password: str = Field(nullable=False)
    full_name: Optional[str] = Field(default=None, nullable=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    documents: List["Document"] = Relationship(back_populates="owner")
    chats: List["Chat"] = Relationship(back_populates="owner")

class Document(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    filename: str
    filepath: str
    file_size: int
    page_count: int = Field(default=0)
    status: str = Field(default="processing")
    error_message: Optional[str] = Field(default=None)
    owner_id: str = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: Optional[User] = Relationship(back_populates="documents")

class Chat(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    title: str = Field(default="New Chat")
    is_pinned: bool = Field(default=False)
    owner_id: str = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: Optional[User] = Relationship(back_populates="chats")
    messages: List["Message"] = Relationship(back_populates="chat", sa_relationship_kwargs={"cascade": "all, delete-orphan", "order_by": "Message.created_at"})

class Message(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    chat_id: str = Field(foreign_key="chat.id")
    role: str
    content: str
    sources: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    chat: Optional[Chat] = Relationship(back_populates="messages")
