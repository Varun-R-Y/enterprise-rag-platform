import logging
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus
from app.services.pdf_service import PDFService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)

class IndexingService:
    """
    Orchestration service that manages the end-to-end document indexing pipeline.
    It coordinates:
    1. Extracting text from PDF via PDFService
    2. Generating chunks via ChunkingService
    3. Generating dense vectors via EmbeddingService
    4. Uploading embeddings via QdrantService
    5. Managing document status transitions (PROCESSING, COMPLETED, FAILED)
    """

    def __init__(
        self,
        pdf_service: PDFService | None = None,
        chunking_service: ChunkingService | None = None,
        embedding_service: EmbeddingService | None = None,
        qdrant_service: QdrantService | None = None
    ) -> None:
        """
        Initializes IndexingService with dependency injection.
        """
        self.pdf_service = pdf_service or PDFService()
        self.chunking_service = chunking_service or ChunkingService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.qdrant_service = qdrant_service or QdrantService()

    def index_document(self, db: Session, document: Document) -> None:
        """
        Runs the full indexing pipeline for a given document.
        Changes status to PROCESSING, commits, runs pipeline, and marks as COMPLETED.
        In case of failures, changes status to FAILED and commits.
        """
        logger.info("Starting indexing")

        # 1. Update status to PROCESSING and commit immediately
        try:
            document.status = DocumentStatus.PROCESSING
            db.add(document)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to transition document {document.id} status to PROCESSING: {e}")
            raise e

        # 2. Run the extraction, chunking, embedding and upload stages
        try:
            # Stage A: PDF Extraction
            try:
                pages = self.pdf_service.extract_text(document.file_path)
                logger.info(f"Extracted {len(pages)} pages")
            except Exception as e:
                logger.error(f"PDF extraction failed: {e}")
                raise e

            # Stage B: Chunking
            try:
                chunks = self.chunking_service.chunk_document(
                    document_id=document.id,
                    pages=pages
                )
                logger.info(f"Generated {len(chunks)} chunks")
                document.chunk_count = len(chunks)
            except Exception as e:
                logger.error(f"Chunk generation failed: {e}")
                raise e

            # Stage C: Embedding Generation
            try:
                embedded_chunks = self.embedding_service.embed_chunks(
                    tenant_id=document.tenant_id,
                    chunks=chunks
                )
                logger.info(f"Generated {len(embedded_chunks)} embeddings")
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
                raise e

            # Stage D: Qdrant Upload and Verification
            try:
                uploaded_points = self.qdrant_service.upload_embeddings(
                    chunks=embedded_chunks,
                    original_filename=document.original_filename
                )
                logger.info(f"Uploaded {uploaded_points} vectors")

                # Verify point count matches chunk count
                if uploaded_points != len(chunks):
                    raise ValueError(
                        f"Point count mismatch: expected {len(chunks)} points, but uploaded {uploaded_points}"
                    )
            except Exception as e:
                logger.error(f"Qdrant upload failed: {e}")
                raise e

            # Stage E: Complete transition
            try:
                document.status = DocumentStatus.COMPLETED
                
                # TODO: Set indexed_at timestamp once column is added in migration
                # from datetime import datetime
                # document.indexed_at = datetime.utcnow()

                db.add(document)
                db.commit()
                logger.info("Document indexed successfully")
            except Exception as e:
                logger.error(f"Failed to transition document status to COMPLETED: {e}")
                raise e

        except Exception as main_exception:
            # Handle failure: transition document status to FAILED and rollback
            try:
                db.rollback()
                document.status = DocumentStatus.FAILED
                db.add(document)
                db.commit()
                logger.error("Document status updated to FAILED")
            except Exception as rollback_err:
                logger.critical(f"Failed to update document status to FAILED for document {document.id}: {rollback_err}")
            
            # Re-raise original exception to preserve traceability
            raise main_exception
