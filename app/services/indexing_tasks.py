import uuid
import logging
import time
from app.database.session import SessionLocal
from app.models.document import Document, DocumentStatus
from app.services.indexing_service import IndexingService

logger = logging.getLogger(__name__)

def get_indexing_service() -> IndexingService:
    """
    Factory function to retrieve an IndexingService instance.
    """
    return IndexingService()


def bg_index_document(document_id: uuid.UUID, attempt: int = 1) -> None:
    """
    Background task to run document indexing.
    Decoupled from FastAPI request context.
    """
    logger.info(f"Background indexing started. Document ID: {document_id}, Attempt: {attempt}")
    start_time = time.perf_counter()
    
    db = SessionLocal()
    tenant_id = None
    try:
        # 1. Fetch the document metadata
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            elapsed = time.perf_counter() - start_time
            logger.error(
                f"Document not found. "
                f"Document ID: {document_id}, "
                f"Tenant ID: Unknown, "
                f"Attempt: {attempt}, "
                f"Duration: {elapsed:.2f}s, "
                f"Result: FAILED, "
                f"Reason: Document not found in database."
            )
            return

        tenant_id = document.tenant_id

        # 2. Run the indexing pipeline
        indexing_service = get_indexing_service()
        indexing_service.index_document(db, document)
        
        elapsed = time.perf_counter() - start_time
        logger.info(
            f"Indexing completed. "
            f"Document ID: {document_id}, "
            f"Tenant ID: {tenant_id}, "
            f"Attempt: {attempt}, "
            f"Duration: {elapsed:.2f}s, "
            f"Result: COMPLETED"
        )
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        logger.exception(
            f"Indexing failed. "
            f"Document ID: {document_id}, "
            f"Tenant ID: {tenant_id if tenant_id else 'Unknown'}, "
            f"Attempt: {attempt}, "
            f"Duration: {elapsed:.2f}s, "
            f"Result: FAILED"
        )
        
        # 3. Fallback: Make sure document status is set to FAILED if the pipeline threw before updating it
        try:
            db.rollback()
            document = db.query(Document).filter(Document.id == document_id).first()
            if document and document.status != DocumentStatus.FAILED:
                document.status = DocumentStatus.FAILED
                db.add(document)
                db.commit()
                logger.info(
                    f"Fallback status update. "
                    f"Document ID: {document_id}, "
                    f"Tenant ID: {tenant_id if tenant_id else 'Unknown'}, "
                    f"Attempt: {attempt}, "
                    f"Result: FAILED_STATUS_UPDATED"
                )
        except Exception as rollback_err:
            logger.critical(
                f"Fallback failure. "
                f"Document ID: {document_id}, "
                f"Tenant ID: {tenant_id if tenant_id else 'Unknown'}, "
                f"Attempt: {attempt}, "
                f"Error: {rollback_err}"
            )
    finally:
        db.close()
