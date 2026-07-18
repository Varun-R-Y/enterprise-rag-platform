import uuid
import pytest
from datetime import datetime, timedelta
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.models.user import User
from app.models.document import Document, DocumentStatus

@pytest.fixture
def create_tenant_and_user(client: TestClient, db_session: Session):
    def _create(email: str, tenant_slug: str):
        tenant_id = uuid.uuid4()
        tenant = Tenant(id=tenant_id, name=f"Tenant {tenant_slug}", slug=tenant_slug)
        db_session.add(tenant)
        db_session.commit()

        user_data = {
            "email": email,
            "password": "strongpassword123",
            "full_name": f"User {email}",
            "tenant_id": str(tenant_id)
        }
        client.post("/auth/register", json=user_data)

        login_data = {
            "username": email,
            "password": "strongpassword123"
        }
        login_response = client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        db_session.rollback()
        return {"Authorization": f"Bearer {token}"}, tenant_id
    return _create


def test_list_documents_success(client: TestClient, db_session: Session, create_tenant_and_user):
    headers, tenant_id = create_tenant_and_user("user1@example.com", "tenant-1")

    # Retrieve the user id created during registration to associate as uploader
    user = db_session.query(User).filter(User.email == "user1@example.com").first()
    assert user is not None

    # Create multiple documents with different creation times to test ordering
    doc1 = Document(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        uploaded_by=user.id,
        title="Doc 1",
        original_filename="doc1.pdf",
        stored_filename="stored1.pdf",
        file_path="uploads/stored1.pdf",
        file_size=1024,
        mime_type="application/pdf",
        status=DocumentStatus.COMPLETED,
        chunk_count=5,
        created_at=datetime.utcnow() - timedelta(hours=1)
    )
    doc2 = Document(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        uploaded_by=user.id,
        title="Doc 2",
        original_filename="doc2.pdf",
        stored_filename="stored2.pdf",
        file_path="uploads/stored2.pdf",
        file_size=2048,
        mime_type="application/pdf",
        status=DocumentStatus.COMPLETED,
        chunk_count=10,
        created_at=datetime.utcnow() # Newest
    )
    
    db_session.add_all([doc1, doc2])
    db_session.commit()

    response = client.get("/documents", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data) == 2
    
    # Doc 2 is newest and should be first
    assert data[0]["id"] == str(doc2.id)
    assert data[0]["original_filename"] == "doc2.pdf"
    assert data[0]["status"] == DocumentStatus.COMPLETED.value
    assert data[0]["chunk_count"] == 10
    assert "uploaded_at" in data[0]

    # Doc 1 is second
    assert data[1]["id"] == str(doc1.id)
    assert data[1]["original_filename"] == "doc1.pdf"
    assert data[1]["status"] == DocumentStatus.COMPLETED.value
    assert data[1]["chunk_count"] == 5


def test_list_documents_empty(client: TestClient, create_tenant_and_user):
    headers, _ = create_tenant_and_user("user_empty@example.com", "tenant-empty")

    response = client.get("/documents", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data == []


def test_list_documents_unauthorized(client: TestClient):
    response = client.get("/documents")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_documents_tenant_isolation(client: TestClient, db_session: Session, create_tenant_and_user):
    headers_a, tenant_a_id = create_tenant_and_user("user_a@example.com", "tenant-a")
    headers_b, tenant_b_id = create_tenant_and_user("user_b@example.com", "tenant-b")

    user_b = db_session.query(User).filter(User.email == "user_b@example.com").first()
    assert user_b is not None

    # Create document under tenant B only
    doc_b = Document(
        id=uuid.uuid4(),
        tenant_id=tenant_b_id,
        uploaded_by=user_b.id,
        title="Doc B",
        original_filename="doc_b.pdf",
        stored_filename="stored_b.pdf",
        file_path="uploads/stored_b.pdf",
        file_size=512,
        mime_type="application/pdf",
        status=DocumentStatus.COMPLETED,
        chunk_count=3
    )
    db_session.add(doc_b)
    db_session.commit()

    # User A requests documents -> should get empty list
    response_a = client.get("/documents", headers=headers_a)
    assert response_a.status_code == status.HTTP_200_OK
    assert response_a.json() == []

    # User B requests documents -> should get their document
    response_b = client.get("/documents", headers=headers_b)
    assert response_b.status_code == status.HTTP_200_OK
    data_b = response_b.json()
    assert len(data_b) == 1
    assert data_b[0]["id"] == str(doc_b.id)


def test_list_documents_with_failed_status(client: TestClient, db_session: Session, create_tenant_and_user):
    headers, tenant_id = create_tenant_and_user("user_failed@example.com", "tenant-failed")

    user = db_session.query(User).filter(User.email == "user_failed@example.com").first()
    assert user is not None

    doc_failed = Document(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        uploaded_by=user.id,
        title="Failed Doc",
        original_filename="failed.pdf",
        stored_filename="stored_failed.pdf",
        file_path="uploads/stored_failed.pdf",
        file_size=1234,
        mime_type="application/pdf",
        status=DocumentStatus.FAILED,
        chunk_count=0
    )
    db_session.add(doc_failed)
    db_session.commit()

    response = client.get("/documents", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(doc_failed.id)
    assert data[0]["status"] == DocumentStatus.FAILED.value
    assert data[0]["chunk_count"] == 0


def test_download_document_success(client: TestClient, db_session: Session, create_tenant_and_user, tmp_path):
    headers, tenant_id = create_tenant_and_user("user_dl@example.com", "tenant-dl")
    user = db_session.query(User).filter(User.email == "user_dl@example.com").first()
    assert user is not None

    dummy_file = tmp_path / "test.pdf"
    dummy_file.write_bytes(b"%PDF-1.4 dummy content")

    doc = Document(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        uploaded_by=user.id,
        title="Download Doc",
        original_filename="original_test.pdf",
        stored_filename="stored_test.pdf",
        file_path=str(dummy_file.as_posix()),
        file_size=len(b"%PDF-1.4 dummy content"),
        mime_type="application/pdf",
        status=DocumentStatus.COMPLETED,
        chunk_count=2
    )
    db_session.add(doc)
    db_session.commit()

    response = client.get(f"/documents/{doc.id}/download", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.content == b"%PDF-1.4 dummy content"
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert "original_test.pdf" in response.headers["content-disposition"]


def test_download_document_not_found(client: TestClient, create_tenant_and_user):
    headers, _ = create_tenant_and_user("user_dl_nf@example.com", "tenant-dl-nf")
    non_existent_id = uuid.uuid4()
    
    response = client.get(f"/documents/{non_existent_id}/download", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Document not found."


def test_download_document_tenant_isolation(client: TestClient, db_session: Session, create_tenant_and_user, tmp_path):
    headers_a, tenant_a_id = create_tenant_and_user("user_dl_a@example.com", "tenant-dl-a")
    headers_b, tenant_b_id = create_tenant_and_user("user_dl_b@example.com", "tenant-dl-b")

    user_b = db_session.query(User).filter(User.email == "user_dl_b@example.com").first()
    assert user_b is not None

    dummy_file = tmp_path / "test_b.pdf"
    dummy_file.write_bytes(b"%PDF-1.4 tenant b content")

    doc_b = Document(
        id=uuid.uuid4(),
        tenant_id=tenant_b_id,
        uploaded_by=user_b.id,
        title="Doc B",
        original_filename="doc_b.pdf",
        stored_filename="stored_b.pdf",
        file_path=str(dummy_file.as_posix()),
        file_size=len(b"%PDF-1.4 tenant b content"),
        mime_type="application/pdf",
        status=DocumentStatus.COMPLETED,
        chunk_count=1
    )
    db_session.add(doc_b)
    db_session.commit()

    # User A tries to download User B's document -> 404
    response_a = client.get(f"/documents/{doc_b.id}/download", headers=headers_a)
    assert response_a.status_code == status.HTTP_404_NOT_FOUND

    # User B tries to download -> 200
    response_b = client.get(f"/documents/{doc_b.id}/download", headers=headers_b)
    assert response_b.status_code == status.HTTP_200_OK
    assert response_b.content == b"%PDF-1.4 tenant b content"
