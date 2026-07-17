import uuid
import pytest
from unittest.mock import MagicMock
from qdrant_client.http.models import ScoredPoint

from app.schemas.document import RetrieveResult
from app.services.retrieval_service import RetrievalService


def test_retrieval_service_success():
    # Arrange
    tenant_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    question = "How do I access NovaTech resources?"
    dummy_vector = [0.1] * 384

    # Mock EmbeddingService
    mock_embedding_service = MagicMock()
    mock_embedding_service.embed_query.return_value = dummy_vector

    # Mock QdrantService client
    mock_qdrant_service = MagicMock()
    mock_qdrant_client = MagicMock()
    mock_qdrant_service.client = mock_qdrant_client

    # Define mock ScoredPoints
    mock_points = [
        ScoredPoint(
            id=str(uuid.uuid4()),
            version=1,
            score=0.92,
            payload={
                "tenant_id": str(tenant_id),
                "document_id": str(doc_id),
                "original_filename": "NovaTech_Handbook.pdf",
                "page": 1,
                "chunk_number": 0,
                "text": "This is page one text.",
            },
        ),
        ScoredPoint(
            id=str(uuid.uuid4()),
            version=1,
            score=0.88,
            payload={
                "tenant_id": str(tenant_id),
                "document_id": str(doc_id),
                "original_filename": "NovaTech_Handbook.pdf",
                "page": 2,
                "chunk_number": 1,
                "text": "This is page two text.",
            },
        ),
    ]
    
    mock_response = MagicMock()
    mock_response.points = mock_points
    mock_qdrant_client.query_points.return_value = mock_response

    retrieval_service = RetrievalService(
        embedding_service=mock_embedding_service,
        qdrant_service=mock_qdrant_service,
    )

    # Act
    results = retrieval_service.retrieve(
        tenant_id=tenant_id,
        question=question,
        top_k=2,
        score_threshold=0.5,
    )

    # Assert
    # 1. Embedding was generated
    mock_embedding_service.embed_query.assert_called_once_with(question)

    # 2. Qdrant search was executed with correct arguments
    mock_qdrant_client.query_points.assert_called_once()
    kwargs = mock_qdrant_client.query_points.call_args[1]
    assert kwargs["collection_name"] == "enterprise_documents"
    assert kwargs["query"] == dummy_vector
    assert kwargs["limit"] == 2
    assert kwargs["score_threshold"] == 0.5
    assert kwargs["with_payload"] is True
    assert kwargs["with_vectors"] is False

    # Check filter is built correctly
    filter_must = kwargs["query_filter"].must
    assert len(filter_must) == 1
    assert filter_must[0].key == "tenant_id"
    assert filter_must[0].match.value == str(tenant_id)

    # 3. Output is mapped correctly to RetrieveResult
    assert len(results) == 2
    assert all(isinstance(r, RetrieveResult) for r in results)
    
    assert results[0].score == 0.92
    assert results[0].tenant_id == tenant_id
    assert results[0].document_id == doc_id
    assert results[0].title == "NovaTech_Handbook.pdf"
    assert results[0].original_filename == "NovaTech_Handbook.pdf"
    assert results[0].page == 1
    assert results[0].chunk_number == 0
    assert results[0].text == "This is page one text."

    assert results[1].score == 0.88
    assert results[1].page == 2
    assert results[1].chunk_number == 1
    assert results[1].text == "This is page two text."


def test_retrieval_service_robust_payload_validation():
    # Arrange
    tenant_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    question = "Query with corrupt data in Qdrant"

    mock_embedding_service = MagicMock()
    mock_embedding_service.embed_query.return_value = [0.1] * 384

    mock_qdrant_service = MagicMock()
    mock_qdrant_client = MagicMock()
    mock_qdrant_service.client = mock_qdrant_client

    # Points with missing/malformed payloads
    mock_points = [
        # Point 1: Missing payload altogether (None)
        ScoredPoint(
            id=str(uuid.uuid4()),
            version=1,
            score=0.95,
            payload=None,
        ),
        # Point 2: Missing key fields (text)
        ScoredPoint(
            id=str(uuid.uuid4()),
            version=1,
            score=0.90,
            payload={
                "tenant_id": str(tenant_id),
                "document_id": str(doc_id),
                "original_filename": "Test.pdf",
                "page": 1,
                "chunk_number": 0,
            },
        ),
        # Point 3: Missing document_id
        ScoredPoint(
            id=str(uuid.uuid4()),
            version=1,
            score=0.85,
            payload={
                "tenant_id": str(tenant_id),
                "original_filename": "Test.pdf",
                "page": 1,
                "chunk_number": 0,
                "text": "Testing",
            },
        ),
        # Point 4: Valid payload
        ScoredPoint(
            id=str(uuid.uuid4()),
            version=1,
            score=0.80,
            payload={
                "tenant_id": str(tenant_id),
                "document_id": str(doc_id),
                "original_filename": "Test.pdf",
                "page": 2,
                "chunk_number": 1,
                "text": "Valid text segment.",
            },
        ),
    ]
    
    mock_response = MagicMock()
    mock_response.points = mock_points
    mock_qdrant_client.query_points.return_value = mock_response

    retrieval_service = RetrievalService(
        embedding_service=mock_embedding_service,
        qdrant_service=mock_qdrant_service,
    )

    # Act
    results = retrieval_service.retrieve(
        tenant_id=tenant_id,
        question=question,
        top_k=5,
    )

    # Assert
    # Only Point 4 should be parsed successfully
    assert len(results) == 1
    assert results[0].score == 0.80
    assert results[0].text == "Valid text segment."
    assert results[0].title == "Test.pdf"
