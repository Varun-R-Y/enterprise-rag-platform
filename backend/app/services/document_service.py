import uuid
import logging
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)

from app.models.document import Document, DocumentStatus
from app.models.user import User

def upload_document(db: Session, file: UploadFile, user: User) -> Document:
    """
    Validates the uploaded file, saves it to disk under the tenant's subdirectory,
    and registers the metadata in the database.
    
    Only PDF files are accepted (extension and MIME-type verified).
    """
    # 1. Validate PDF file type
    filename = file.filename or ""
    
    # Verify extension ends with .pdf
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed."
        )
        
    # Verify MIME type is application/pdf
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed."
        )

    # 2. Setup upload folder structure under uploads/<tenant_id>/
    tenant_id = user.tenant_id
    uploads_dir = Path("uploads") / str(tenant_id)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    # 3. Generate UUID filename for storage
    stored_filename = f"{uuid.uuid4()}.pdf"
    file_path = uploads_dir / stored_filename

    # 4. Save file to disk
    try:
        # Determine the file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        # Save file in chunks to optimize memory usage
        with open(file_path, "wb") as buffer:
            while content := file.file.read(1024 * 1024):  # 1MB chunks
                buffer.write(content)
    except Exception as e:
        # Ensure any partially written file is removed
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )

    # 5. Create Document record in database
    # Derive title from original filename (using stem)
    title = Path(filename).stem or "Untitled Document"

    document = Document(
        tenant_id=tenant_id,
        uploaded_by=user.id,
        title=title,
        original_filename=filename,
        stored_filename=stored_filename,
        file_path=str(file_path.as_posix()),  # Save path in standard forward-slash format
        file_size=file_size,
        mime_type=file.content_type,
        status=DocumentStatus.PROCESSING
    )

    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception as e:
        # Cleanup the saved file on DB write failure to maintain system consistency
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error saving document metadata: {str(e)}"
        )

    return document


def list_documents(db: Session, tenant_id: uuid.UUID) -> list[Document]:
    """
    Retrieves all documents belonging to a specific tenant, ordered by created_at DESC.
    """
    return (
        db.query(Document)
        .filter(Document.tenant_id == tenant_id)
        .order_by(Document.created_at.desc())
        .all()
    )


class DocumentNotFoundError(Exception):
    """
    Raised when a requested document does not exist or belongs to another tenant.
    """
    pass


def delete_document(
    db: Session,
    tenant_id: uuid.UUID,
    document_id: uuid.UUID,
    qdrant_service: QdrantService | None = None
) -> int:
    """
    Orchestrates the secure deletion of a document:
    1. Finds document by ID and verifies tenant ownership.
    2. Deletes all associated vectors from Qdrant.
    3. Deletes document record from Postgres and commits.
    4. After successful commit, deletes the local file from storage.
    
    If the file is already missing locally, continues without failing.
    If file deletion fails (e.g. permissions/locking), logs warning and continues.
    """
    # 1. Find document by ID
    document = db.query(Document).filter(Document.id == document_id).first()
    
    # 2. Tenant isolation verify
    if not document or document.tenant_id != tenant_id:
        raise DocumentNotFoundError("Document not found.")

    # 3. Delete vectors belonging to this document from Qdrant
    q_service = qdrant_service or QdrantService()
    try:
        vectors_deleted = q_service.delete_document_embeddings(tenant_id=tenant_id, document_id=document_id)
    except Exception as e:
        logger.error(f"Failed to delete embeddings from Qdrant: {e}")
        raise e

    # Store file path before database deletion
    file_path = Path(document.file_path)

    # 4. Delete database record & commit
    try:
        db.delete(document)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error deleting document metadata: {e}")
        raise e

    # 5. Delete uploaded PDF from local storage
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Local file deleted: {file_path}")
        else:
            logger.warning(f"Local file already missing (continuing without failing): {file_path}")
    except Exception as e:
        logger.warning(f"Error deleting file from local storage: {e}. Document record has already been removed.")

    return vectors_deleted

