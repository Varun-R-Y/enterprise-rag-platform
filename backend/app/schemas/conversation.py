from datetime import datetime
from typing import Any
from pydantic import BaseModel, UUID4

class ConversationCreate(BaseModel):
    title: str = "New Chat"

class ConversationUpdate(BaseModel):
    title: str

class ConversationSummary(BaseModel):
    id: UUID4
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int

    class Config:
        from_attributes = True

class MessageOut(BaseModel):
    id: UUID4
    role: str
    content: str
    citations: Any = None
    created_at: datetime

    class Config:
        from_attributes = True
