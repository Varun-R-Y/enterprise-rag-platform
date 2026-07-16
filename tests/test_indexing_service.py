import uuid
import pytest
import logging
from unittest.mock import MagicMock

from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.models.document import Document, DocumentStatus
from app.schemas.document import PageContent, Chunk, EmbeddedChunk
from app.services.indexing_service import IndexingService

def test_indexing_service_success(db_session, caplog):
    # Setup log capturing
    caplog.set_level(logging.INFO)

    # 1. Arrange
    # Create required Database entries
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, name="Test Tenant", slug="test-tenant")
    db_session.add(tenant)
    db_session.commit()

    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        tenant_id=tenant_id,
        full_name="John Doe",
        email="john@example.com",
        hashed_password="some_hashed_password",
        role=UserRole.EMPLOYEE
    )
    db_session.add(user)
    db_session.commit()

    document = Document(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        uploaded_by=user_id,
        title="Test Document",
        original_filename="NovaTech_Employee_Handbook_v1.pdf",
        stored_filename="stored.pdf",
        file_path="uploads/stored.pdf",
        file_size=100,
        mime_type="application/pdf",
        status=DocumentStatus.PENDING
    )
    db_session.add(document)
    db_session.commit()

    # Create mock sub-services
    mock_pdf = MagicMock()
    mock_pdf.extract_text.return_value = [
        PageContent(page=1, text="Page one content."),
        PageContent(page=2, text="Page two content.")
    ]

    mock_chunking = MagicMock()
    mock_chunking.chunk_document.return_value = [
        Chunk(document_id=document.id, page=1, chunk_number=0, text="Page one content."),
        Chunk(document_id=document.id, page=2, chunk_number=1, text="Page two content.")
    ]

    mock_embedding = MagicMock()
    mock_embedding.embed_chunks.return_value = [
        EmbeddedChunk(
            tenant_id=tenant_id,
            document_id=document.id,
            page=1,
            chunk_number=0,
            text="Page one content.",
            vector=[0.1] * 384
        ),
        EmbeddedChunk(
            tenant_id=tenant_id,
            document_id=document.id,
            page=2,
            chunk_number=1,
            text="Page two content.",
            vector=[0.2] * 384
        )
    ]

    mock_qdrant = MagicMock()
    # Mock return value to be the exact number of chunks (2)
    mock_qdrant.upload_embeddings.return_value = 2

    # Instantiate IndexingService with mocks
    indexing_service = IndexingService(
        pdf_service=mock_pdf,
        chunking_service=mock_chunking,
        embedding_service=mock_embedding,
        qdrant_service=mock_qdrant
    )

    # 2. Act
    indexing_service.index_document(db_session, document)

    # 3. Assert
    # Verify status changed to COMPLETED in the database
    db_session.refresh(document)
    assert document.status == DocumentStatus.COMPLETED

    # Verify calls
    mock_pdf.extract_text.assert_called_once_with("uploads/stored.pdf")
    mock_chunking.chunk_document.assert_called_once()
    mock_embedding.embed_chunks.assert_called_once()
    mock_qdrant.upload_embeddings.assert_called_once()

    # Verify logs
    log_messages = [record.message for record in caplog.records]
    assert any("Starting indexing" in msg for msg in log_messages)
    assert any("Extracted 2 pages" in msg for msg in log_messages)
    assert any("Generated 2 chunks" in msg for msg in log_messages)
    assert any("Generated 2 embeddings" in msg for msg in log_messages)
    assert any("Uploaded 2 vectors" in msg for msg in log_messages)
    assert any("Document indexed successfully" in msg for msg in log_messages)


def test_indexing_service_failure(db_session, caplog):
    # Setup log capturing
    caplog.set_level(logging.INFO)

    # 1. Arrange
    # Create required Database entries
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, name="Test Tenant 2", slug="test-tenant-2")
    db_session.add(tenant)
    db_session.commit()

    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        tenant_id=tenant_id,
        full_name="Jane Doe",
        email="jane@example.com",
        hashed_password="some_hashed_password",
        role=UserRole.EMPLOYEE
    )
    db_session.add(user)
    db_session.commit()

    document = Document(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        uploaded_by=user_id,
        title="Test Doc Fail",
        original_filename="Fail_Handbook.pdf",
        stored_filename="stored_fail.pdf",
        file_path="uploads/stored_fail.pdf",
        file_size=100,
        mime_type="application/pdf",
        status=DocumentStatus.PENDING
    )
    db_session.add(document)
    db_session.commit()

    # Mock PDF service to succeed
    mock_pdf = MagicMock()
    mock_pdf.extract_text.return_value = [PageContent(page=1, text="Text")]

    # Mock Chunking service to succeed
    mock_chunking = MagicMock()
    mock_chunking.chunk_document.return_value = [Chunk(document_id=document.id, page=1, chunk_number=0, text="Text")]

    # Mock Embedding service to fail
    mock_embedding = MagicMock()
    mock_embedding.embed_chunks.side_effect = RuntimeError("GPU Out of Memory")

    mock_qdrant = MagicMock()

    indexing_service = IndexingService(
        pdf_service=mock_pdf,
        chunking_service=mock_chunking,
        embedding_service=mock_embedding,
        qdrant_service=mock_qdrant
    )

    # 2. Act & Assert
    with pytest.raises(RuntimeError) as exc_info:
        indexing_service.index_document(db_session, document)
    
    assert "GPU Out of Memory" in str(exc_info.value)

    # Verify status changed to FAILED in the database
    db_session.refresh(document)
    assert document.status == DocumentStatus.FAILED

    # Verify logs
    log_messages = [record.message for record in caplog.records]
    assert any("Starting indexing" in msg for msg in log_messages)
    assert any("Extracted 1 pages" in msg for msg in log_messages)
    assert any("Generated 1 chunks" in msg for msg in log_messages)
    assert any("Embedding generation failed" in msg for msg in log_messages)
    assert any("Document status updated to FAILED" in msg for msg in log_messages)
