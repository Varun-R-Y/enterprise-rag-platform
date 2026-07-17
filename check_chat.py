import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure app modules can be imported
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

load_dotenv()

# Setup logging to output INFO
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

from app.database.session import SessionLocal
from app.models.document import Document, DocumentStatus
from app.services.chat_service import ChatService


async def main():
    db = SessionLocal()
    
    # 1. Fetch tenant_id and document from DB
    doc = db.query(Document).filter(Document.status == DocumentStatus.COMPLETED).first()
    if not doc:
        doc = db.query(Document).first()
        
    if not doc:
        print("WARNING: No documents found in database. Please run indexing first.")
        print("Falling back to a random tenant UUID for demonstration.")
        import uuid
        tenant_id = uuid.uuid4()
    else:
        tenant_id = doc.tenant_id
        print(f"Using Tenant ID: {tenant_id}")
        print(f"Using Document: '{doc.original_filename}' (Status: {doc.status})")

    db.close()

    # 2. Initialize ChatService
    chat_service = ChatService()

    question = "How many casual leave days do employees receive?"
    print(f"\n--- User Question ---")
    print(question)
    print("---------------------\n")

    # 3. Call ChatService
    try:
        response = await chat_service.chat(
            tenant_id=tenant_id,
            question=question,
            top_k=3,
            score_threshold=0.3
        )
    except Exception as e:
        print(f"Error during chat orchestration: {e}")
        sys.exit(1)

    # 4. Display results
    print("\n--- RAG Response ---")
    print(response.answer)
    print("--------------------\n")

    print("--- Sources & Citations ---")
    if not response.sources:
        print("No sources cited.")
    for i, src in enumerate(response.sources, 1):
        print(f"[{i}] Document: {src.document} | Page: {src.page} | Score: {src.score:.4f}")
    print("---------------------------\n")
    print("Execution completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
