import pytest
import httpx
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.llm.ollama_service import OllamaService


@pytest.mark.anyio
async def test_ollama_generate_success():
    # Arrange
    service = OllamaService()
    prompt = "Test prompt"
    expected_response = "Generated Response"

    with patch("httpx.AsyncClient") as MockClientClass:
        # Set up mock client instance
        mock_client = AsyncMock()
        MockClientClass.return_value.__aenter__.return_value = mock_client

        # Set up mock response
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": expected_response}
        
        # AsyncMock returning mock response
        mock_client.post.return_value = mock_response

        # Act
        result = await service.generate(prompt)

        # Assert
        assert result == expected_response
        mock_client.post.assert_called_once()
        args, kwargs = mock_client.post.call_args
        assert kwargs["json"]["prompt"] == prompt
        assert kwargs["json"]["stream"] is False


@pytest.mark.anyio
async def test_ollama_generate_empty_prompt():
    service = OllamaService()

    # Empty prompt
    with pytest.raises(ValueError) as exc_info:
        await service.generate("")
    assert "Prompt cannot be empty" in str(exc_info.value)

    # Whitespace-only prompt
    with pytest.raises(ValueError) as exc_info:
        await service.generate("   ")
    assert "Prompt cannot be empty" in str(exc_info.value)


@pytest.mark.anyio
async def test_ollama_generate_connection_error():
    service = OllamaService()

    with patch("httpx.AsyncClient") as MockClientClass:
        mock_client = AsyncMock()
        MockClientClass.return_value.__aenter__.return_value = mock_client
        mock_client.post.side_effect = httpx.ConnectError("Connection refused")

        with pytest.raises(RuntimeError) as exc_info:
            await service.generate("Hello")
        assert "server is unavailable" in str(exc_info.value)


@pytest.mark.anyio
async def test_ollama_generate_timeout():
    service = OllamaService()

    with patch("httpx.AsyncClient") as MockClientClass:
        mock_client = AsyncMock()
        MockClientClass.return_value.__aenter__.return_value = mock_client
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")

        with pytest.raises(RuntimeError) as exc_info:
            await service.generate("Hello")
        assert "timed out" in str(exc_info.value)


@pytest.mark.anyio
async def test_ollama_generate_invalid_json():
    service = OllamaService()

    with patch("httpx.AsyncClient") as MockClientClass:
        mock_client = AsyncMock()
        MockClientClass.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        # JSON parsing throws ValueError
        mock_response.json.side_effect = ValueError("No JSON object could be decoded")
        mock_client.post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            await service.generate("Hello")
        assert "Invalid JSON response" in str(exc_info.value)


@pytest.mark.anyio
async def test_ollama_generate_missing_response_field():
    service = OllamaService()

    with patch("httpx.AsyncClient") as MockClientClass:
        mock_client = AsyncMock()
        MockClientClass.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        # Missing response field in payload
        mock_response.json.return_value = {"status": "success"}
        mock_client.post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            await service.generate("Hello")
        assert "Missing 'response' field" in str(exc_info.value)


@pytest.mark.anyio
async def test_ollama_generate_http_status_error():
    service = OllamaService()

    with patch("httpx.AsyncClient") as MockClientClass:
        mock_client = AsyncMock()
        MockClientClass.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="Internal Server Error",
            request=MagicMock(spec=httpx.Request),
            response=mock_response
        )
        mock_client.post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            await service.generate("Hello")
        assert "Ollama server returned HTTP error: 500" in str(exc_info.value)

