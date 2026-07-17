import time
import logging
from uuid import UUID

from app.schemas.chat import Source, ChatResponse
from app.services.retrieval_service import RetrievalService
from app.services.prompt_builder import PromptBuilder
from app.services.llm.base import BaseLLM
from app.services.llm.ollama_service import OllamaService

logger = logging.getLogger(__name__)


class ChatService:
    """
    Orchestration service that coordinates:
    1. Retrieval of semantically similar chunks via RetrievalService.
    2. Building of LLM prompts via PromptBuilder.
    3. Generating responses using the LLM model (BaseLLM).
    4. Mapping sources to deterministic citations.
    """

    def __init__(
        self,
        retrieval_service: RetrievalService | None = None,
        prompt_builder: PromptBuilder | None = None,
        llm: BaseLLM | None = None,
    ) -> None:
        """
        Initializes ChatService with dependency injection.
        """
        self.retrieval_service = retrieval_service or RetrievalService()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.llm = llm or OllamaService()

    async def chat(
        self,
        tenant_id: UUID,
        question: str,
        top_k: int = 5,
        score_threshold: float | None = None,
    ) -> ChatResponse:
        """
        Processes a user's question, retrieves context documents, constructs the prompt,
        queries the LLM, and returns the response with references.

        Args:
            tenant_id: UUID of the tenant.
            question: The user's question string.
            top_k: Maximum number of semantic chunks to retrieve.
            score_threshold: Optional similarity threshold for retrieval.

        Returns:
            A ChatResponse containing the answer and citation sources.
        """
        # Step 1: Validate input question
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        logger.info(f"Question received. Length: {len(question)} characters.")
        start_time = time.perf_counter()

        # Step 2: Retrieve chunks
        chunks = self.retrieval_service.retrieve(
            tenant_id=tenant_id,
            question=question,
            top_k=top_k,
            score_threshold=score_threshold,
        )
        logger.info(f"Retrieved {len(chunks)} chunk(s).")

        # Step 3: Fast-fail if no chunks were found
        if not chunks:
            elapsed_time = time.perf_counter() - start_time
            logger.info(
                f"No chunks retrieved. Returning default response. "
                f"Total execution time: {elapsed_time:.2f} seconds."
            )
            return ChatResponse(
                answer="I could not find that information in the provided documents.",
                sources=[],
            )

        # Step 4: Construct prompt
        prompt = self.prompt_builder.build_prompt(question, chunks)
        logger.info(f"Prompt generated. Length: {len(prompt)} characters.")

        # Step 5: Execute LLM generation
        try:
            answer = await self.llm.generate(prompt)
            logger.info("LLM response received.")
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise e

        # Step 6: Map citations deterministically
        sources = [
            Source(
                document=chunk.original_filename,
                page=chunk.page,
                score=chunk.score,
            )
            for chunk in chunks
        ]

        # Step 7: Complete orchestration and log metrics
        elapsed_time = time.perf_counter() - start_time
        logger.info(f"Total execution time: {elapsed_time:.2f} seconds.")

        return ChatResponse(
            answer=answer,
            sources=sources,
        )
