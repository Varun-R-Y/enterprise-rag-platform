from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole

def list_conversations(db: Session, tenant_id: uuid.UUID, user_id: uuid.UUID, page: int = 1, limit: int = 20) -> list[Conversation]:
    """
    Retrieves a paginated list of conversations for a user, sorted by updated_at DESC.
    """
    offset = (page - 1) * limit
    return (
        db.query(Conversation)
        .filter(Conversation.tenant_id == tenant_id, Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def get_message_count(db: Session, conversation_id: uuid.UUID) -> int:
    """
    Counts the messages in a conversation.
    """
    return db.query(Message).filter(Message.conversation_id == conversation_id).count()

def create_conversation(db: Session, tenant_id: uuid.UUID, user_id: uuid.UUID, title: str = "New Chat") -> Conversation:
    """
    Creates a new conversation.
    """
    conversation = Conversation(
        tenant_id=tenant_id,
        user_id=user_id,
        title=title
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def get_conversation(db: Session, tenant_id: uuid.UUID, user_id: uuid.UUID, conversation_id: uuid.UUID) -> Conversation | None:
    """
    Retrieves a conversation verifying tenant and user ownership.
    """
    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
            Conversation.user_id == user_id
        )
        .first()
    )

def update_conversation(db: Session, tenant_id: uuid.UUID, user_id: uuid.UUID, conversation_id: uuid.UUID, title: str) -> Conversation | None:
    """
    Updates the conversation properties (title).
    """
    conversation = get_conversation(db, tenant_id, user_id, conversation_id)
    if not conversation:
        return None
    conversation.title = title
    conversation.updated_at = func.now()
    db.commit()
    db.refresh(conversation)
    return conversation

def delete_conversation(db: Session, tenant_id: uuid.UUID, user_id: uuid.UUID, conversation_id: uuid.UUID) -> bool:
    """
    Deletes a conversation by ID.
    """
    conversation = get_conversation(db, tenant_id, user_id, conversation_id)
    if not conversation:
        return False
    db.delete(conversation)
    db.commit()
    return True

def get_messages(db: Session, conversation_id: uuid.UUID) -> list[Message]:
    """
    Retrieves messages sorted explicitly by created_at ASC.
    """
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

def add_message(db: Session, conversation_id: uuid.UUID, role: str, content: str, citations: list | dict | None = None) -> Message:
    """
    Appends a message to the database and updates conversation updated_at.
    Auto-updates the title from "New Chat" on the first message.
    """
    msg_count = get_message_count(db, conversation_id)
    
    message = Message(
        conversation_id=conversation_id,
        role=MessageRole(role),
        content=content,
        citations=citations
    )
    db.add(message)
    
    # Update the conversation updated_at and rename if needed
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.updated_at = func.now()
        # Rename "New Chat" using a snippet of the first user question
        if msg_count == 0 and role == "user" and conversation.title == "New Chat":
            title_text = content.strip()
            if len(title_text) > 40:
                title_text = title_text[:37] + "..."
            conversation.title = title_text or "New Chat"
            
    db.commit()
    db.refresh(message)
    return message
