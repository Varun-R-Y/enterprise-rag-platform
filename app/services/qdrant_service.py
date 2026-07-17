import sys
import logging
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.core.config import settings
from app.schemas.document import EmbeddedChunk

logger = logging.getLogger(__name__)

# A stable UUID namespace specifically for generating chunk point IDs.
# Ensures that uuid.uuid5 outputs are stable and distinct for our platform.
CHUNKS_NAMESPACE = uuid.UUID("a2345678-1234-5678-1234-567812345678")

class QdrantService:
    """
    Service to interact with the Qdrant vector database.
    Handles collection management and document chunk embeddings upload.
    """

    def __init__(self) -> None:
        """
        Initializes the QdrantClient with QDRANT_URL and QDRANT_API_KEY.
        Raises ValueError if either configuration is missing.
        """
        if not settings.QDRANT_URL:
            raise ValueError("QDRANT_URL is not set in environment settings.")
        if not settings.QDRANT_API_KEY:
            raise ValueError("QDRANT_API_KEY is not set in environment settings.")

        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )

    def create_collection(self) -> None:
        """
        Creates the 'enterprise_documents' collection in Qdrant if it doesn't already exist.
        Configuration:
          - Vector size: 384
          - Distance: Cosine
        """
        collection_name = "enterprise_documents"
        
        try:
            # Check if collection exists
            exists = self.client.collection_exists(collection_name=collection_name)
        except AttributeError:
            # Fallback for older versions of qdrant-client
            try:
                self.client.get_collection(collection_name=collection_name)
                exists = True
            except Exception:
                exists = False

        if exists:
            logger.info(f"Collection '{collection_name}' already exists. Skipping creation.")
            return

        logger.info(f"Creating collection '{collection_name}'...")
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=384,
                distance=models.Distance.COSINE
            )
        )
        # Create payload index for tenant_id filtering
        self.client.create_payload_index(
            collection_name=collection_name,
            field_name="tenant_id",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        logger.info(f"Collection '{collection_name}' created successfully and payload index on 'tenant_id' initialized.")

    def upload_embeddings(self, chunks: list[EmbeddedChunk], original_filename: str) -> int:
        """
        Uploads a list of EmbeddedChunks to Qdrant using batch upload.
        Generates stable, deterministic point IDs based on document_id and chunk_number.
        Returns the number of points successfully uploaded.
        """
        if not chunks:
            logger.warning("Empty list of chunks provided for upload.")
            return 0

        collection_name = "enterprise_documents"
        points = []

        for chunk in chunks:
            # Generate deterministic UUID (stable ID) using UUIDv5
            # Combines document_id and chunk_number under our platform namespace
            stable_input = f"{chunk.document_id}_{chunk.chunk_number}"
            point_id = str(uuid.uuid5(CHUNKS_NAMESPACE, stable_input))

            payload = {
                "tenant_id": str(chunk.tenant_id),
                "document_id": str(chunk.document_id),
                "page": int(chunk.page),
                "chunk_number": int(chunk.chunk_number),
                "text": str(chunk.text),
                "original_filename": str(original_filename)
            }

            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=chunk.vector,
                    payload=payload
                )
            )

        logger.info(f"Uploading {len(points)} embeddings to collection '{collection_name}'...")
        self.client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True
        )
        logger.info(f"Successfully uploaded {len(points)} embeddings to Qdrant.")
        return len(points)


if __name__ == "__main__":
    from dotenv import load_dotenv

    # Load environment variables from .env for the standalone run
    load_dotenv()

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    print("Starting QdrantService standalone example...")
    try:
        service = QdrantService()
        
        # 1. Create collection
        service.create_collection()

        # 2. Mock some EmbeddedChunk objects
        sample_tenant_id = uuid.uuid4()
        sample_doc_id = uuid.uuid4()
        
        # Create a mock 384-dimensional vector
        dummy_vector = [0.1] * 384
        
        mock_chunks = [
            EmbeddedChunk(
                tenant_id=sample_tenant_id,
                document_id=sample_doc_id,
                page=1,
                chunk_number=0,
                text="This is a test chunk for the Qdrant service.",
                vector=dummy_vector
            ),
            EmbeddedChunk(
                tenant_id=sample_tenant_id,
                document_id=sample_doc_id,
                page=2,
                chunk_number=1,
                text="Another mock chunk for checking stable point ID upserts.",
                vector=dummy_vector
            )
        ]

        # 3. Upload embeddings
        print("Uploading dummy embeddings...")
        service.upload_embeddings(mock_chunks, original_filename="Test_Handbook.pdf")
        print("Standalone example run completed successfully!")
    except Exception as e:
        print(f"Error during standalone example run: {e}")
        sys.exit(1)
