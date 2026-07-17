import uuid
import logging
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.document import DocumentUploadResponse, DocumentSummary
from app.services.document_service import upload_document, list_documents, delete_document, DocumentNotFoundError
from app.services.indexing_tasks import bg_index_document

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a PDF document",
    description="Accepts only PDF files, saves them under tenant directory and stores metadata."
)
def upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DocumentUploadResponse:
    """
    Endpoint to upload PDF documents. Thin controller containing no business logic.
    """
    document = upload_document(db=db, file=file, user=current_user)
    logger.info(f"Upload received. Document ID: {document.id}")
    background_tasks.add_task(bg_index_document, document.id)
    return DocumentUploadResponse(
        document_id=document.id,
        message="Document uploaded and indexing started"
    )


@router.get(
    "",
    response_model=list[DocumentSummary],
    summary="List tenant documents",
    description="Lists all documents belonging to the authenticated user's tenant, sorted by uploaded_at DESC."
)
def list_tenant_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[DocumentSummary]:
    """
    Endpoint to list PDF documents for the user's tenant.
    """
    documents = list_documents(db=db, tenant_id=current_user.tenant_id)
    
    logger.info(
        f"Authenticated user ID: {current_user.id}, "
        f"Tenant ID: {current_user.tenant_id}, "
        f"Number of documents returned: {len(documents)}"
    )

    return [
        DocumentSummary(
            id=doc.id,
            original_filename=doc.original_filename,
            status=doc.status,
            uploaded_at=doc.created_at,
            chunk_count=doc.chunk_count
        )
        for doc in documents
    ]


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
    description="Deletes a document and its associated vectors and file securely."
)
def delete_tenant_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Endpoint to delete a document and its associated vectors and file.
    """
    try:
        vectors_deleted = delete_document(db=db, tenant_id=current_user.tenant_id, document_id=document_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    logger.info(
        f"User ID: {current_user.id}, "
        f"Tenant ID: {current_user.tenant_id}, "
        f"Document ID: {document_id}, "
        f"Number of vectors deleted: {vectors_deleted}, "
        f"Deletion completed"
    )

