import time
import asyncio
import logging
import httpx
from app.core.config import settings
from app.services.llm.base import BaseLLM

logger = logging.getLogger(__name__)


class OllamaService(BaseLLM):
    """
    Service to communicate with a local Ollama HTTP API instance.
    Includes retry logic with exponential backoff for transient failures.
    """

    GENERATE_ENDPOINT = "/api/generate"
    MAX_RETRIES = 3
    BASE_BACKOFF_SECONDS = 1.0  # 1s, 2s, 4s

    async def generate(self, prompt: str) -> str:
        """
        Asynchronously sends the prompt to local Ollama and returns the response.
        Retries up to MAX_RETRIES times on connection errors and timeouts.

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

        last_exception = None
        start = time.perf_counter()

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=15.0)) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()

                # Success — break out of retry loop
                elapsed = time.perf_counter() - start
                logger.info(f"Received response successfully on attempt {attempt}.")
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

            except httpx.ConnectError as e:
                last_exception = e
                logger.warning(
                    f"Attempt {attempt}/{self.MAX_RETRIES}: Could not connect to Ollama at "
                    f"{settings.OLLAMA_BASE_URL}: {e}"
                )
            except httpx.TimeoutException as e:
                last_exception = e
                logger.warning(
                    f"Attempt {attempt}/{self.MAX_RETRIES}: Request to Ollama timed out: {e}"
                )
            except httpx.HTTPStatusError as e:
                # HTTP errors (4xx/5xx) are not retried — they indicate a real problem
                logger.error(f"Ollama HTTP error occurred: Status {e.response.status_code}")
                raise RuntimeError(f"Ollama server returned HTTP error: {e.response.status_code}") from e
            except httpx.RequestError as e:
                last_exception = e
                logger.warning(
                    f"Attempt {attempt}/{self.MAX_RETRIES}: Communication error with Ollama: {e}"
                )

            # Exponential backoff before next retry
            if attempt < self.MAX_RETRIES:
                backoff = self.BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
                logger.info(f"Retrying in {backoff:.1f}s...")
                await asyncio.sleep(backoff)

        # All retries exhausted
        logger.error(f"All {self.MAX_RETRIES} attempts to reach Ollama failed.")
        if isinstance(last_exception, httpx.ConnectError):
            raise RuntimeError(
                f"Ollama server is unavailable at {settings.OLLAMA_BASE_URL} after {self.MAX_RETRIES} retries."
            ) from last_exception
        elif isinstance(last_exception, httpx.TimeoutException):
            raise RuntimeError(
                f"Request to Ollama timed out after {self.MAX_RETRIES} retries."
            ) from last_exception
        else:
            raise RuntimeError(
                f"Failed to communicate with Ollama after {self.MAX_RETRIES} retries: {last_exception}"
            ) from last_exception

