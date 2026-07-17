import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure app modules can be imported
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

load_dotenv()

# Setup logging to output INFO messages
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

from app.database.session import SessionLocal
from app.models.document import Document, DocumentStatus
from app.services.retrieval_service import RetrievalService


def main():
    db = SessionLocal()
    
    # 1. Fetch a document from the database to identify a tenant_id and test document
    doc = db.query(Document).filter(Document.status == DocumentStatus.COMPLETED).first()
    if not doc:
        # If no completed document is found, fall back to any document
        doc = db.query(Document).first()
        
    if not doc:
        print("WARNING: No documents found in database. Please run indexing first.")
        print("Falling back to a random tenant UUID for demonstration.")
        import uuid
        tenant_id = uuid.uuid4()
    else:
        tenant_id = doc.tenant_id
        print(f"Using Tenant ID: {tenant_id}")
        print(f"Found document: '{doc.original_filename}' (Status: {doc.status})")

    db.close()

    # 2. Initialize RetrievalService
    retrieval_service = RetrievalService()

    # 3. Prompt user for query or use default
    default_question = "What are the employee benefits and holiday policies?"
    print(f"\nEntering query: '{default_question}'")

    # 4. Perform retrieval
    try:
        results = retrieval_service.retrieve(
            tenant_id=tenant_id,
            question=default_question,
            top_k=3,
            score_threshold=0.3
        )
    except Exception as e:
        print(f"Error during retrieval: {e}")
        sys.exit(1)

    # 5. Output results
    print(f"\n--- Retrieved {len(results)} chunks matching the query ---")
    if not results:
        print("No matching chunks found. (Either empty collection or low scores/mismatched tenant_id)")
    
    for i, res in enumerate(results, 1):
        print(f"\n[{i}] Score: {res.score:.4f}")
        print(f"    Document ID: {res.document_id}")
        print(f"    Title: {res.title}")
        print(f"    Filename: {res.original_filename}")
        print(f"    Page: {res.page} | Chunk: {res.chunk_number}")
        print(f"    Text snippet:")
        print(f"    \"\"\"{res.text[:300]}...\"\"\"")
    print("\n-----------------------------------------------------")


if __name__ == "__main__":
    main()
