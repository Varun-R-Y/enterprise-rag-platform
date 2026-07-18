import io
import uuid
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch

from app.models.tenant import Tenant
from app.models.document import Document, DocumentStatus

@pytest.fixture
def auth_headers(client: TestClient, db_session: Session):
    """
    Creates a tenant and a user, logs them in, and returns headers containing the JWT token.
    """
    # 1. Create a dummy tenant
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, name="Test Tenant", slug="test-tenant")
    db_session.add(tenant)
    db_session.commit()

    # 2. Register user
    user_data = {
        "email": "user@example.com",
        "password": "strongpassword123",
        "full_name": "John Doe",
        "tenant_id": str(tenant_id)
    }
    client.post("/auth/register", json=user_data)

    # 3. Log in to get token
    login_data = {
        "username": "user@example.com",
        "password": "strongpassword123"
    }
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    db_session.rollback()
    return {"Authorization": f"Bearer {token}"}, tenant_id

def test_upload_pdf_success(client: TestClient, db_session: Session, auth_headers):
    headers, tenant_id = auth_headers
    
    # Create fake PDF binary content
    pdf_content = b"%PDF-1.4 ... fake pdf content ..."
    file_name = "test_document.pdf"
    
    files = {
        "file": (file_name, io.BytesIO(pdf_content), "application/pdf")
    }
    
    with patch("app.api.document.bg_index_document") as mock_bg_task:
        response = client.post("/documents/upload", headers=headers, files=files)
        assert response.status_code == 202
        
        resp_json = response.json()
        assert "document_id" in resp_json
        assert resp_json["message"] == "Document uploaded and indexing started"
        
        doc_id = resp_json["document_id"]
        
        # Verify database record
        db_doc = db_session.query(Document).filter(Document.id == uuid.UUID(doc_id)).first()
        assert db_doc is not None
        assert db_doc.tenant_id == tenant_id
        assert db_doc.original_filename == "test_document.pdf"
        assert db_doc.title == "test_document"
        assert db_doc.mime_type == "application/pdf"
        assert db_doc.status == DocumentStatus.PROCESSING
        assert db_doc.file_size == len(pdf_content)
        
        # Verify background task scheduled
        mock_bg_task.assert_called_once_with(db_doc.id)
        
        # Verify file saved on disk
        file_path = Path(db_doc.file_path)
        assert file_path.exists()
        assert file_path.read_bytes() == pdf_content
        
        # Cleanup disk files
        if file_path.exists():
            file_path.unlink()
            # Clean up tenant folder if empty
            if file_path.parent.exists() and not any(file_path.parent.iterdir()):
                file_path.parent.rmdir()

def test_upload_non_pdf_fails(client: TestClient, auth_headers):
    headers, _ = auth_headers
    
    # 1. Invalid extension but correct MIME type (e.g. .exe but application/pdf)
    files = {
        "file": ("malicious.exe", io.BytesIO(b"dummy content"), "application/pdf")
    }
    response = client.post("/documents/upload", headers=headers, files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed."
    
    # 2. Correct extension but invalid MIME type (e.g. .pdf but text/plain)
    files = {
        "file": ("document.pdf", io.BytesIO(b"dummy content"), "text/plain")
    }
    response = client.post("/documents/upload", headers=headers, files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed."
    
    # 3. Both wrong
    files = {
        "file": ("virus.exe", io.BytesIO(b"dummy content"), "application/x-msdownload")
    }
    response = client.post("/documents/upload", headers=headers, files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed."

def test_upload_unauthorized(client: TestClient):
    pdf_content = b"%PDF-1.4 dummy"
    files = {
        "file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")
    }
    
    # No headers
    response = client.post("/documents/upload", files=files)
    assert response.status_code == 401
    
    # Bad token
    bad_headers = {"Authorization": "Bearer badtoken"}
    response = client.post("/documents/upload", headers=bad_headers, files=files)
    assert response.status_code == 401
