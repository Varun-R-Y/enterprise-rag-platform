import logging
from typing import Any
from qdrant_client.http import models

from app.schemas.document import RetrieveResult
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Service responsible for semantic retrieval from Qdrant vector database.
    It generates embeddings for user queries and searches Qdrant,
    applying tenant filtering and score thresholding.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        qdrant_service: QdrantService | None = None,
    ) -> None:
        """
        Initializes the RetrievalService with dependency injection.
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.qdrant_service = qdrant_service or QdrantService()

    def retrieve(
        self,
        tenant_id: Any,
        question: str,
        top_k: int = 5,
        score_threshold: float | None = None,
    ) -> list[RetrieveResult]:
        """
        Retrieves the top_k most semantically similar chunks for the tenant's question.

        Args:
            tenant_id: The UUID or string ID of the tenant.
            question: The search query text.
            top_k: The maximum number of similar chunks to return.
            score_threshold: Optional similarity score threshold filter.

        Returns:
            A list of RetrieveResult models.
        """
        logger.info(f"Embedding question: '{question[:50]}...'")
        query_vector = self.embedding_service.embed_query(question)

        logger.info("Searching Qdrant collection 'enterprise_documents'...")
        
        # Build tenant filter
        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="tenant_id",
                    match=models.MatchValue(value=str(tenant_id)),
                )
            ]
        )

        try:
            # In qdrant-client v1.18.0, query_points is the unified method for retrieval.
            response = self.qdrant_service.client.query_points(
                collection_name="enterprise_documents",
                query=query_vector,
                query_filter=query_filter,
                limit=top_k,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False,
            )
            qdrant_results = response.points
        except Exception as e:
            logger.error(f"Failed to query Qdrant collection: {e}")
            raise e

        results = []
        for point in qdrant_results:
            payload = point.payload
            if payload is None:
                logger.warning(f"Qdrant point {point.id} has no payload. Skipping.")
                continue

            tenant_id_val = payload.get("tenant_id")
            doc_id_val = payload.get("document_id")
            original_filename = payload.get("original_filename")
            page_val = payload.get("page")
            chunk_num_val = payload.get("chunk_number")
            text_val = payload.get("text")

            # Validate minimum required payload fields are present
            if not doc_id_val or not tenant_id_val or text_val is None:
                logger.warning(
                    f"Point {point.id} payload is missing required fields "
                    f"(tenant_id, document_id, or text). Skipping."
                )
                continue

            # Keep simple title derivation: title = original_filename
            title_val = original_filename or "Untitled Document"

            try:
                result = RetrieveResult(
                    score=point.score,
                    tenant_id=tenant_id_val,
                    document_id=doc_id_val,
                    title=title_val,
                    original_filename=original_filename or "Unknown",
                    page=int(page_val) if page_val is not None else 0,
                    chunk_number=int(chunk_num_val) if chunk_num_val is not None else 0,
                    text=str(text_val),
                )
                results.append(result)
            except Exception as e:
                logger.error(
                    f"Validation error mapping point {point.id} payload to RetrieveResult: {e}"
                )
                continue

        logger.info(f"Retrieved {len(results)} chunks.")
        return results
