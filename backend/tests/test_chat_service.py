import uuid
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.schemas.document import RetrieveResult
from app.schemas.chat import ChatResponse
from app.services.chat_service import ChatService


@pytest.mark.anyio
async def test_chat_service_success():
    # Arrange
    tenant_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    question = "How many casual leave days do employees receive?"
    
    # Mock RetrieveResults
    mock_chunks = [
        RetrieveResult(
            score=0.95,
            tenant_id=tenant_id,
            document_id=doc_id,
            title="Handbook",
            original_filename="Handbook.pdf",
            page=2,
            chunk_number=0,
            text="Employees receive 12 casual leave days."
        )
    ]

    mock_retrieval_service = MagicMock()
    mock_retrieval_service.retrieve.return_value = mock_chunks

    mock_prompt_builder = MagicMock()
    mock_prompt_builder.build_prompt.return_value = "Formatted Prompt"

    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "Model response: 12 days."

    service = ChatService(
        retrieval_service=mock_retrieval_service,
        prompt_builder=mock_prompt_builder,
        llm=mock_llm
    )

    # Act
    response = await service.chat(
        tenant_id=tenant_id,
        question=question,
        top_k=5,
        score_threshold=0.5
    )

    # Assert
    assert isinstance(response, ChatResponse)
    assert response.answer == "Model response: 12 days."
    assert len(response.sources) == 1
    assert response.sources[0].document == "Handbook.pdf"
    assert response.sources[0].page == 2
    assert response.sources[0].score == 0.95

    # Verify orchestration calls
    mock_retrieval_service.retrieve.assert_called_once_with(
        tenant_id=tenant_id,
        question=question,
        top_k=5,
        score_threshold=0.5
    )
    mock_prompt_builder.build_prompt.assert_called_once_with(
        question,
        mock_chunks,
        None
    )
    mock_llm.generate.assert_called_once_with("Formatted Prompt")


@pytest.mark.anyio
async def test_chat_service_empty_question():
    # Arrange
    tenant_id = uuid.uuid4()
    service = ChatService()

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        await service.chat(tenant_id, "")
    assert "Question cannot be empty" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        await service.chat(tenant_id, "   ")
    assert "Question cannot be empty" in str(exc_info.value)


@pytest.mark.anyio
async def test_chat_service_no_retrieved_chunks():
    # Arrange
    tenant_id = uuid.uuid4()
    question = "Some query with no records"

    mock_retrieval_service = MagicMock()
    mock_retrieval_service.retrieve.return_value = []

    mock_prompt_builder = MagicMock()
    mock_llm = AsyncMock()

    service = ChatService(
        retrieval_service=mock_retrieval_service,
        prompt_builder=mock_prompt_builder,
        llm=mock_llm
    )

    # Act
    response = await service.chat(tenant_id, question)

    # Assert
    assert isinstance(response, ChatResponse)
    assert response.answer == "I could not find that information in the provided documents."
    assert response.sources == []

    # Verify calls
    mock_retrieval_service.retrieve.assert_called_once()
    mock_prompt_builder.build_prompt.assert_not_called()
    mock_llm.generate.assert_not_called()


@pytest.mark.anyio
async def test_chat_service_llm_failure_propagation():
    # Arrange
    tenant_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    question = "A question that breaks"

    mock_chunks = [
        RetrieveResult(
            score=0.90,
            tenant_id=tenant_id,
            document_id=doc_id,
            title="Handbook",
            original_filename="Handbook.pdf",
            page=2,
            chunk_number=0,
            text="Context info."
        )
    ]

    mock_retrieval_service = MagicMock()
    mock_retrieval_service.retrieve.return_value = mock_chunks

    mock_prompt_builder = MagicMock()
    mock_prompt_builder.build_prompt.return_value = "Formatted Prompt"

    mock_llm = AsyncMock()
    # LLM fails
    mock_llm.generate.side_effect = RuntimeError("Ollama failure")

    service = ChatService(
        retrieval_service=mock_retrieval_service,
        prompt_builder=mock_prompt_builder,
        llm=mock_llm
    )

    # Act & Assert
    with pytest.raises(RuntimeError) as exc_info:
        await service.chat(tenant_id, question)
    assert "Ollama failure" in str(exc_info.value)
