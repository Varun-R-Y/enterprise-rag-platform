import sys
import uuid
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure app modules can be imported by adding the project root to sys.path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

load_dotenv()

# Setup logging to output level INFO and message only
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s  %(message)s"
)

from app.database.session import SessionLocal
from app.models.tenant import Tenant
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.services.indexing_service import IndexingService

def locate_pdf() -> Path:
    # 1. Local workspace root
    local_path = project_root / "NovaTech_Employee_Handbook_v1.pdf"
    if local_path.exists():
        return local_path

    # 2. Database lookup
    try:
        db = SessionLocal()
        doc = db.query(Document).filter(Document.original_filename == "NovaTech_Employee_Handbook_v1.pdf").first()
        if doc:
            db_path = project_root / doc.file_path
            if db_path.exists():
                db.close()
                return db_path
        db.close()
    except Exception:
        pass

    # 3. Scan uploads directory
    uploads_dir = project_root / "uploads"
    if uploads_dir.exists():
        pdf_files = list(uploads_dir.glob("**/*.pdf"))
        for pf in pdf_files:
            if pf.name == "NovaTech_Employee_Handbook_v1.pdf":
                return pf
        if pdf_files:
            return pdf_files[0]

    print("Error: Could not find NovaTech_Employee_Handbook_v1.pdf or any other PDF file.")
    sys.exit(1)

def main():
    db = SessionLocal()
    
    # 1. Ensure a Tenant and User exist in DB for test purposes
    tenant = db.query(Tenant).first()
    if not tenant:
        print("Creating mock tenant...")
        tenant = Tenant(id=uuid.uuid4(), name="Test Tenant", slug="test-tenant")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    user = db.query(User).filter(User.tenant_id == tenant.id).first()
    if not user:
        print("Creating mock user...")
        user = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            full_name="Indexing Tester",
            email="indexer@example.com",
            hashed_password="hashed_pw_here"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Locate PDF
    pdf_path = locate_pdf()
    print(f"Using PDF file: {pdf_path}")

    # 3. Create a Document record in PENDING status
    document = Document(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        uploaded_by=user.id,
        title=pdf_path.stem,
        original_filename="NovaTech_Employee_Handbook_v1.pdf",
        stored_filename=pdf_path.name,
        file_path=str(pdf_path.as_posix()),
        file_size=pdf_path.stat().st_size,
        mime_type="application/pdf",
        status=DocumentStatus.PENDING
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    print(f"Created Document record: {document.id} in PENDING state.\n")

    # 4. Instantiate IndexingService and run pipeline
    indexing_service = IndexingService()
    try:
        indexing_service.index_document(db, document)
        db.refresh(document)
        print(f"\nSuccess! Final Document status in DB: {document.status}")
    except Exception as e:
        db.refresh(document)
        print(f"\nIndexing failed! Final Document status in DB: {document.status}")
        print(f"Exception raised: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
