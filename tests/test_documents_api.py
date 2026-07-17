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
        
        return {"Authorization": f"Bearer {token}"}, tenant_id
    return _create


def test_list_documents_success(client: TestClient, db_session: Session, create_tenant_and_user):
    headers, tenant_id = create_tenant_and_user("user1@example.com", "tenant-1")

    # Retrieve the user id created during registration to associate as uploader
    user = db_session.query(User).filter(User.email == "user1@example.com").first()

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
