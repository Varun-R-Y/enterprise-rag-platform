import io
import uuid
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.services.indexing_tasks import bg_index_document
from main import app
from tests.conftest import TestingSessionLocal

@pytest.fixture
def auth_headers(client: TestClient, db_session: Session):
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, name="Test Tenant BG", slug="test-tenant-bg")
    db_session.add(tenant)
    db_session.commit()

    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    
    # Directly create user in database as admin to allow upload trigger
    user = User(
        email="bg_user@example.com",
        hashed_password=get_password_hash("strongpassword123"),
        full_name="BG User",
        tenant_id=tenant_id,
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    login_data = {
        "username": "bg_user@example.com",
        "password": "strongpassword123"
    }
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    db_session.rollback()
    return {"Authorization": f"Bearer {token}"}, tenant_id


def test_upload_schedules_background_task_and_returns_202(client: TestClient, db_session: Session, auth_headers):
    headers, tenant_id = auth_headers
    pdf_content = b"%PDF-1.4 ... fake pdf content ..."

    # Mock bg_index_document to prevent real indexing run
    with patch("app.api.document.bg_index_document") as mock_bg_task:
        files = {
            "file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")
        }

        # Act
        response = client.post("/documents/upload", headers=headers, files=files)
        
        # Assert
        assert response.status_code == status.HTTP_202_ACCEPTED
        resp_json = response.json()
        assert "document_id" in resp_json
        assert resp_json["message"] == "Document uploaded and indexing started"

        # Verify DB status is immediately PROCESSING
        doc_id = uuid.UUID(resp_json["document_id"])
        db_doc = db_session.query(Document).filter(Document.id == doc_id).first()
        assert db_doc is not None
        assert db_doc.status == DocumentStatus.PROCESSING

        # Verify background task was scheduled
        mock_bg_task.assert_called_once_with(db_doc.id)


def test_bg_indexing_success(db_session: Session):
    # Setup document
    tenant_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    doc = Document(
        id=doc_id,
        tenant_id=tenant_id,
        title="Test Doc",
        original_filename="test.pdf",
        stored_filename="stored.pdf",
        file_path="uploads/test.pdf",
        file_size=100,
        mime_type="application/pdf",
        status=DocumentStatus.PROCESSING
    )
    db_session.add(doc)
    db_session.commit()

    # Mock IndexingService.index_document to change status to COMPLETED
    def mock_index(db, document):
        document.status = DocumentStatus.COMPLETED
        db.add(document)
        db.commit()

    with patch("app.services.indexing_tasks.get_indexing_service") as MockGetIndexingService, \
         patch("app.services.indexing_tasks.SessionLocal", side_effect=TestingSessionLocal):
        
        mock_indexing_instance = MagicMock()
        mock_indexing_instance.index_document.side_effect = mock_index
        MockGetIndexingService.return_value = mock_indexing_instance

        # Act
        bg_index_document(doc_id)

        # Assert
        db_session.refresh(doc)
        assert doc.status == DocumentStatus.COMPLETED


def test_bg_indexing_failure(db_session: Session):
    # Setup document
    tenant_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    doc = Document(
        id=doc_id,
        tenant_id=tenant_id,
        title="Test Doc",
        original_filename="test.pdf",
        stored_filename="stored.pdf",
        file_path="uploads/test.pdf",
        file_size=100,
        mime_type="application/pdf",
        status=DocumentStatus.PROCESSING
    )
    db_session.add(doc)
    db_session.commit()

    # Mock IndexingService.index_document to raise exception
    with patch("app.services.indexing_tasks.get_indexing_service") as MockGetIndexingService, \
         patch("app.services.indexing_tasks.SessionLocal", side_effect=TestingSessionLocal):
        
        mock_indexing_instance = MagicMock()
        mock_indexing_instance.index_document.side_effect = Exception("Indexing pipeline crash")
        MockGetIndexingService.return_value = mock_indexing_instance

        # Act
        bg_index_document(doc_id)

        # Assert
        db_session.refresh(doc)
        assert doc.status == DocumentStatus.FAILED


def test_bg_indexing_pre_start_crash(db_session: Session):
    # Setup document
    tenant_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    doc = Document(
        id=doc_id,
        tenant_id=tenant_id,
        title="Test Doc Crash",
        original_filename="test_crash.pdf",
        stored_filename="stored_crash.pdf",
        file_path="uploads/test_crash.pdf",
        file_size=100,
        mime_type="application/pdf",
        status=DocumentStatus.PROCESSING
    )
    db_session.add(doc)
    db_session.commit()

    # Mock get_indexing_service to raise an exception before indexing starts
    with patch("app.services.indexing_tasks.get_indexing_service", side_effect=Exception("Pre-start factory failure")), \
         patch("app.services.indexing_tasks.SessionLocal", side_effect=TestingSessionLocal):
        
        # Act
        bg_index_document(doc_id)

        # Assert
        db_session.refresh(doc)
        assert doc.status == DocumentStatus.FAILED
