import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.conversation import ConversationCreate, ConversationUpdate, ConversationSummary, MessageOut
from app.services import conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.get("", response_model=list[ConversationSummary])
def get_conversations(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[ConversationSummary]:
    """
    List tenant conversations for the authenticated user, paginated.
    """
    conversations = conversation_service.list_conversations(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        page=page,
        limit=limit
    )
    
    summaries = []
    for conv in conversations:
        count = conversation_service.get_message_count(db, conv.id)
        summaries.append(
            ConversationSummary(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=count
            )
        )
    return summaries

@router.post("", response_model=ConversationSummary, status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ConversationSummary:
    """
    Create a new conversation session.
    """
    conv = conversation_service.create_conversation(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        title=payload.title
    )
    return ConversationSummary(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=0
    )

@router.get("/{conversation_id}", response_model=ConversationSummary)
def get_conversation_metadata(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ConversationSummary:
    """
    Get conversation metadata.
    """
    conv = conversation_service.get_conversation(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        conversation_id=conversation_id
    )
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found."
        )
    count = conversation_service.get_message_count(db, conv.id)
    return ConversationSummary(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=count
    )

@router.patch("/{conversation_id}", response_model=ConversationSummary)
def rename_conversation(
    conversation_id: uuid.UUID,
    payload: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ConversationSummary:
    """
    Rename/Update a conversation title.
    """
    conv = conversation_service.update_conversation(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        conversation_id=conversation_id,
        title=payload.title
    )
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found."
        )
    count = conversation_service.get_message_count(db, conv.id)
    return ConversationSummary(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=count
    )

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a conversation and all its messages.
    """
    success = conversation_service.delete_conversation(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        conversation_id=conversation_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found."
        )

@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def get_conversation_messages(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[MessageOut]:
    """
    Get messages for a conversation, sorted ASC by creation date.
    """
    conv = conversation_service.get_conversation(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        conversation_id=conversation_id
    )
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found."
        )
    
    messages = conversation_service.get_messages(db, conversation_id)
    return [
        MessageOut(
            id=msg.id,
            role=msg.role.value,
            content=msg.content,
            citations=msg.citations,
            created_at=msg.created_at
        )
        for msg in messages
    ]
