import time
import logging
import httpx
from app.core.config import settings
from app.services.llm.base import BaseLLM

logger = logging.getLogger(__name__)


class OllamaService(BaseLLM):
    """
    Service to communicate with a local Ollama HTTP API instance.
    """

    GENERATE_ENDPOINT = "/api/generate"

    async def generate(self, prompt: str) -> str:
        """
        Asynchronously sends the prompt to local Ollama and returns the response.

        Args:
            prompt: The full prompt string to send.

        Returns:
            The generated response string from the model.

        Raises:
            ValueError: If the prompt is empty or whitespace-only.
            RuntimeError: For connection issues, timeouts, invalid JSON,
                         or missing fields in the response.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        url = f"{settings.OLLAMA_BASE_URL}{self.GENERATE_ENDPOINT}"

        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        }

        logger.info("Sending request to Ollama...")
        logger.info(f"Model: {settings.OLLAMA_MODEL}")
        logger.info(f"Prompt length: {len(prompt)} characters")

        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
        except httpx.ConnectError as e:
            logger.error(f"Could not connect to Ollama server at {settings.OLLAMA_BASE_URL}: {e}")
            raise RuntimeError(
                f"Ollama server is unavailable at {settings.OLLAMA_BASE_URL}."
            ) from e
        except httpx.TimeoutException as e:
            logger.error(f"Request to Ollama server timed out after 60.0 seconds: {e}")
            raise RuntimeError("Request to Ollama timed out.") from e
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error occurred: Status {response.status_code}")
            raise RuntimeError(f"Ollama server returned HTTP error: {response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"Error during request communication with Ollama: {e}")
            raise RuntimeError(f"Failed to communicate with Ollama: {e}") from e

        elapsed = time.perf_counter() - start
        logger.info("Received response successfully.")
        logger.info(f"Generation time: {elapsed:.2f} seconds")

        try:
            data = response.json()
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to parse Ollama response as JSON: {e}")
            raise RuntimeError("Invalid JSON response received from Ollama.") from e

        if not isinstance(data, dict) or "response" not in data:
            logger.error(f"Ollama response JSON is missing expected 'response' field. Data: {data}")
            raise RuntimeError("Missing 'response' field in Ollama output.")

        return str(data["response"])
