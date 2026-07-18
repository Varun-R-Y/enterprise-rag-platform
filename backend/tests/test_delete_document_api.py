import uuid
import pytest
from pathlib import Path
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from main import app

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


def test_delete_document_success(client: TestClient, db_session: Session, create_tenant_and_user):
    headers, tenant_id = create_tenant_and_user("user_del@example.com", "tenant-del")
    user = db_session.query(User).filter(User.email == "user_del@example.com").first()
    assert user is not None

    doc = Document(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        uploaded_by=user.id,
        title="To Delete",
        original_filename="delete_me.pdf",
        stored_filename="stored_del.pdf",
        file_path="uploads/stored_del.pdf",
        file_size=100,
        mime_type="application/pdf",
        status=DocumentStatus.COMPLETED,
        chunk_count=5
    )
    db_session.add(doc)
    db_session.commit()

    with patch("app.services.document_service.QdrantService") as MockQdrantClass, \
         patch("app.services.document_service.Path.exists", return_value=True) as mock_exists, \
         patch("app.services.document_service.Path.unlink") as mock_unlink:
        
        mock_qdrant_instance = MockQdrantClass.return_value
        mock_qdrant_instance.delete_document_embeddings.return_value = 5

        response = client.delete(f"/documents/{doc.id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify Qdrant delete was called
        mock_qdrant_instance.delete_document_embeddings.assert_called_once_with(
            tenant_id=tenant_id, document_id=doc.id
        )

        # Verify file unlink was called
        mock_unlink.assert_called_once()

        # Verify document is removed from database
        deleted_doc = db_session.query(Document).filter(Document.id == doc.id).first()
        assert deleted_doc is None


def test_delete_document_unauthorized(client: TestClient):
    random_id = uuid.uuid4()
    response = client.delete(f"/documents/{random_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_document_tenant_isolation(client: TestClient, db_session: Session, create_tenant_and_user):
    headers_a, tenant_a_id = create_tenant_and_user("user_a@example.com", "tenant-a")
    headers_b, tenant_b_id = create_tenant_and_user("user_b@example.com", "tenant-b")

    user_b = db_session.query(User).filter(User.email == "user_b@example.com").first()
    assert user_b is not None

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

    with patch("app.services.document_service.QdrantService") as MockQdrantClass, \
         patch("app.services.document_service.Path.exists") as mock_exists, \
         patch("app.services.document_service.Path.unlink") as mock_unlink:
        
        mock_qdrant_instance = MockQdrantClass.return_value

        # User A tries to delete Tenant B's document
        response = client.delete(f"/documents/{doc_b.id}", headers=headers_a)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify Qdrant delete was NOT called
        mock_qdrant_instance.delete_document_embeddings.assert_not_called()

        # Verify file was NOT unlinked
        mock_unlink.assert_not_called()

        # Verify document still exists in DB
        doc_still_exists = db_session.query(Document).filter(Document.id == doc_b.id).first()
        assert doc_still_exists is not None


def test_delete_document_missing(client: TestClient, create_tenant_and_user):
    headers, _ = create_tenant_and_user("user_missing@example.com", "tenant-missing")
    random_id = uuid.uuid4()
    response = client.delete(f"/documents/{random_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_document_qdrant_failure(client: TestClient, db_session: Session, create_tenant_and_user):
    headers, tenant_id = create_tenant_and_user("user_fail@example.com", "tenant-fail")
    user = db_session.query(User).filter(User.email == "user_fail@example.com").first()
    assert user is not None

    doc = Document(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        uploaded_by=user.id,
        title="Qdrant Fail",
        original_filename="qdrant_fail.pdf",
        stored_filename="stored_q_fail.pdf",
        file_path="uploads/stored_q_fail.pdf",
        file_size=100,
        mime_type="application/pdf",
        status=DocumentStatus.COMPLETED,
        chunk_count=2
    )
    db_session.add(doc)
    db_session.commit()

    with patch("app.services.document_service.QdrantService") as MockQdrantClass, \
         patch("app.services.document_service.Path.exists", return_value=True) as mock_exists, \
         patch("app.services.document_service.Path.unlink") as mock_unlink:
        
        mock_qdrant_instance = MockQdrantClass.return_value
        mock_qdrant_instance.delete_document_embeddings.side_effect = Exception("Qdrant unavailable")

        # Request delete using local TestClient configuration that suppresses exception raising
        with TestClient(app, raise_server_exceptions=False) as local_client:
            response = local_client.delete(f"/documents/{doc.id}", headers=headers)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        # File was NOT unlinked
        mock_unlink.assert_not_called()

        # Database transaction rolled back and record still exists
        db_session.rollback()  # Sync session state
        doc_in_db = db_session.query(Document).filter(Document.id == doc.id).first()
        assert doc_in_db is not None


def test_delete_document_missing_local_file(client: TestClient, db_session: Session, create_tenant_and_user):
    headers, tenant_id = create_tenant_and_user("user_missing_file@example.com", "tenant-missing-file")
    user = db_session.query(User).filter(User.email == "user_missing_file@example.com").first()
    assert user is not None

    doc = Document(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        uploaded_by=user.id,
        title="Missing Local File",
        original_filename="missing_file.pdf",
        stored_filename="stored_missing.pdf",
        file_path="uploads/stored_missing.pdf",
        file_size=100,
        mime_type="application/pdf",
        status=DocumentStatus.COMPLETED,
        chunk_count=5
    )
    db_session.add(doc)
    db_session.commit()

    with patch("app.services.document_service.QdrantService") as MockQdrantClass, \
         patch("app.services.document_service.Path.exists", return_value=False) as mock_exists, \
         patch("app.services.document_service.Path.unlink") as mock_unlink:
        
        mock_qdrant_instance = MockQdrantClass.return_value
        mock_qdrant_instance.delete_document_embeddings.return_value = 5

        # Execute delete
        response = client.delete(f"/documents/{doc.id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify Qdrant delete was called
        mock_qdrant_instance.delete_document_embeddings.assert_called_once_with(
            tenant_id=tenant_id, document_id=doc.id
        )

        # File unlink was NOT called since it was missing
        mock_unlink.assert_not_called()

        # Document is still deleted from DB
        deleted_doc = db_session.query(Document).filter(Document.id == doc.id).first()
        assert deleted_doc is None
