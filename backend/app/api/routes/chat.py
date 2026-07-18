import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.chat_request import ChatRequest
from app.schemas.chat import ChatResponse
from app.services.chat_service import ChatService
from app.services import conversation_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


def get_chat_service() -> ChatService:
    """
    Dependency provider to retrieve a ChatService instance.
    """
    return ChatService()


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit a question to the Chat assistant",
    description=(
        "Accepts a question, queries semantic search filtered by tenant, "
        "synthesizes the prompt, runs local generation, and returns answer and sources."
    )
)
async def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    """
    Protected chat API route orchestrating semantic search retrieval and LLM response.
    """
    logger.info("Incoming chat request.")
    logger.info(f"Authenticated user ID: {current_user.id}")
    logger.info(f"Tenant ID: {current_user.tenant_id}")

    # Validate conversation_id if present
    if request.conversation_id:
        conv = conversation_service.get_conversation(
            db=db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            conversation_id=request.conversation_id
        )
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found."
            )

    try:
        # Validate question empty/whitespace and other validation errors
        if not request.question or not request.question.strip():
            raise ValueError("Question cannot be empty.")
        if request.top_k < 1:
            raise ValueError("top_k must be greater than or equal to 1.")

        response = await chat_service.chat(
            tenant_id=current_user.tenant_id,
            question=request.question,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
        )

        # Save messages to database if conversation exists
        if request.conversation_id:
            # 1. Add User message
            conversation_service.add_message(
                db=db,
                conversation_id=request.conversation_id,
                role="user",
                content=request.question
            )
            # 2. Add Assistant message (and map sources to JSON structure)
            citations_list = [
                {
                    "document": src.document,
                    "document_id": str(src.document_id),
                    "page": src.page,
                    "score": src.score
                }
                for src in response.sources
            ] if response.sources else []
            
            conversation_service.add_message(
                db=db,
                conversation_id=request.conversation_id,
                role="assistant",
                content=response.answer,
                citations=citations_list
            )

        logger.info("Chat execution completed.")
        return response
    except ValueError as e:
        logger.warning(f"Validation error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException as e:
        # Re-raise FastAPI HTTPExceptions unchanged
        raise e
    except Exception as e:
        logger.exception(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        )
