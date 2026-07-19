import logging
from pydantic import UUID4
from sentence_transformers import SentenceTransformer

from app.schemas.document import Chunk, EmbeddedChunk

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service to generate sentence embeddings for document chunks.
    Uses SentenceTransformers with BAAI/bge-small-en-v1.5.
    Runs on CPU by default.

    The model is loaded once as a class-level singleton and shared
    across all instances to avoid reloading on every request.
    """

    _model: SentenceTransformer | None = None
    _model_name: str = "BAAI/bge-small-en-v1.5"

    @classmethod
    def _get_model(cls) -> SentenceTransformer:
        """Lazy-load the model once and cache it at the class level."""
        if cls._model is None:
            logger.info(f"Loading embedding model: {cls._model_name} (singleton init)")
            cls._model = SentenceTransformer(cls._model_name)
            logger.info("Embedding model loaded successfully.")
        return cls._model

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        # Update class-level model name if a custom one is provided
        if model_name != self.__class__._model_name and self.__class__._model is not None:
            logger.warning(f"Model name changed to {model_name}, but singleton already loaded. Ignoring.")
        self.__class__._model_name = model_name
        self.model = self._get_model()

    def embed_chunks(
        self, tenant_id: UUID4, chunks: list[Chunk], uploaded_by: UUID4 | None = None, batch_size: int = 32
    ) -> list[EmbeddedChunk]:
        """
        Generates normalized embeddings for a list of Chunks in batches.
        Preserves all chunk metadata and assigns the tenant_id.

        Args:
            tenant_id: The UUID of the tenant.
            chunks: List of Chunk models to embed.
            uploaded_by: Optional UUID of the user who uploaded the document.
            batch_size: Size of batches for model encoding.

        Returns:
            A list of EmbeddedChunk models.
        """
        if not chunks:
            return []

        # Extract text from chunks
        texts = [chunk.text for chunk in chunks]

        logger.info(
            f"Encoding {len(chunks)} chunks in batches of {batch_size}..."
        )
        # Generate embeddings in batches, normalized using cosine similarity
        vectors = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        embedded_chunks = []
        for chunk, vector in zip(chunks, vectors):
            embedded_chunk = EmbeddedChunk(
                tenant_id=tenant_id,
                document_id=chunk.document_id,
                page=chunk.page,
                chunk_number=chunk.chunk_number,
                text=chunk.text,
                vector=vector.tolist(), # Convert numpy array to list[float]
                uploaded_by=uploaded_by,
            )
            embedded_chunks.append(embedded_chunk)

        logger.info(f"Successfully generated {len(embedded_chunks)} embedded chunks.")
        return embedded_chunks

    def embed_query(self, text: str) -> list[float]:
        """
        Generates a normalized embedding for a single text query.

        Args:
            text: The text query string.

        Returns:
            A list of floats representing the embedding vector.
        """
        logger.info(f"Generating embedding for query: '{text[:50]}...'")
        vector = self.model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        logger.info("Successfully generated query embedding.")
        return vector.tolist()


if __name__ == "__main__":
    import uuid

    # Setup basic logging
    logging.basicConfig(level=logging.INFO)

    # Example usage:
    # 1. Initialize the embedding service
    embedding_service = EmbeddingService()

    # 2. Mock some chunk data
    sample_tenant_id = uuid.uuid4()
    sample_doc_id = uuid.uuid4()
    sample_chunks = [
        Chunk(
            document_id=sample_doc_id,
            page=1,
            chunk_number=0,
            text="FastAPI is a modern, fast, web framework for building APIs with Python.",
        ),
        Chunk(
            document_id=sample_doc_id,
            page=2,
            chunk_number=1,
            text="SentenceTransformers allows you to easily generate embeddings for sentences.",
        ),
    ]

    # 3. Generate embeddings
    embedded = embedding_service.embed_chunks(
        tenant_id=sample_tenant_id, chunks=sample_chunks
    )

    # 4. Display results
    print(f"\nGenerated {len(embedded)} EmbeddedChunks:")
    for ec in embedded:
        print(f"Chunk #{ec.chunk_number} (Page {ec.page})")
        print(f"Tenant ID: {ec.tenant_id}")
        print(f"Document ID: {ec.document_id}")
        print(f"Text: {ec.text}")
        print(f"Vector Dimensions: {len(ec.vector)}")
        print(f"Vector Preview: {ec.vector[:5]}...")
        print("-" * 50)
