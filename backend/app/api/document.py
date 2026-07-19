import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.deps import get_current_user, require_admin, require_active_tenant_user
from app.models.user import User
from app.models.document import Document
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
    description="Accepts only PDF files, saves them under tenant directory and stores metadata. Admin only."
)
def upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
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
    current_user: User = Depends(require_active_tenant_user)
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
            chunk_count=doc.chunk_count,
            file_size=doc.file_size
        )
        for doc in documents
    ]


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
    description="Deletes a document and its associated vectors and file securely. Admin only."
)
def delete_tenant_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
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


@router.get(
    "/{document_id}/download",
    summary="Download a document",
    description="Streams the original PDF document file with proper authorization."
)
def download_tenant_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_tenant_user)
) -> FileResponse:
    """
    Endpoint to download/stream a PDF document.
    """
    # 1. Look up the document in the database
    document = db.query(Document).filter(Document.id == document_id).first()
    
    # 2. Check if document exists and matches tenant
    if not document or document.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
        
    # 3. Check if local file exists
    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found on server."
        )
        
    # 4. Stream file response
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=document.original_filename
    )

