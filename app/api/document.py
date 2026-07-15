from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.document import DocumentUploadResponse
from app.services.document_service import upload_document

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a PDF document",
    description="Accepts only PDF files, saves them under tenant directory and stores metadata."
)
def upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DocumentUploadResponse:
    """
    Endpoint to upload PDF documents. Thin controller containing no business logic.
    """
    document = upload_document(db=db, file=file, user=current_user)
    return DocumentUploadResponse(
        document_id=document.id,
        message="Document uploaded successfully"
    )
