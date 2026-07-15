import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

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
        status=DocumentStatus.PENDING
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
