import sys
import uuid
import logging
from pathlib import Path

# Setup basic logging configuration to output warnings/errors only
logging.basicConfig(level=logging.WARNING)

# Ensure app modules can be imported by adding the project root to sys.path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.services.pdf_service import PDFService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService

def locate_pdf() -> Path:
    """
    Attempts to find the PDF file NovaTech_Employee_Handbook_v1.pdf.
    Checks:
    1. Local workspace root.
    2. The database to resolve its original filename to its stored path.
    3. Recursively scans the uploads folder.
    """
    # 1. Local workspace root
    local_path = project_root / "NovaTech_Employee_Handbook_v1.pdf"
    if local_path.exists():
        return local_path

    # 2. Database lookup to map original_filename to stored path
    try:
        from app.database.session import SessionLocal
        from app.models.document import Document
        db = SessionLocal()
        doc = db.query(Document).filter(Document.original_filename == "NovaTech_Employee_Handbook_v1.pdf").first()
        if doc:
            db_path = project_root / doc.file_path
            if db_path.exists():
                db.close()
                return db_path
        db.close()
    except Exception:
        # Ignore DB exceptions (e.g., if DB is not running/configured) and fall back
        pass

    # 3. Recursive directory scan of uploads/
    uploads_dir = project_root / "uploads"
    if uploads_dir.exists():
        pdf_files = list(uploads_dir.glob("**/*.pdf"))
        # First check if any file is named NovaTech_Employee_Handbook_v1.pdf
        for pf in pdf_files:
            if pf.name == "NovaTech_Employee_Handbook_v1.pdf":
                return pf
        # Otherwise fall back to any PDF found
        if pdf_files:
            return pdf_files[0]

    print("Error: Could not find NovaTech_Employee_Handbook_v1.pdf or any other PDF file in the uploads/ directory.")
    sys.exit(1)

def main():
    # 1. Locate the sample PDF
    pdf_path = locate_pdf()
    print(f"Loading sample PDF: {pdf_path.name}\n")

    # 2. Extract text using PDFService
    pdf_service = PDFService()
    try:
        pages = pdf_service.extract_text(pdf_path)
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        sys.exit(1)

    # 3. Generate chunks using ChunkingService
    chunking_service = ChunkingService(chunk_size=800, chunk_overlap=150)
    document_id = uuid.uuid4()
    chunks = chunking_service.chunk_document(document_id=document_id, pages=pages)

    # 4. Generate embeddings using EmbeddingService
    embedding_service = EmbeddingService()
    tenant_id = uuid.uuid4()
    
    try:
        embedded_chunks = embedding_service.embed_chunks(tenant_id=tenant_id, chunks=chunks)
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        sys.exit(1)

    # 5. Print the requested information for every embedded chunk
    total_chunks = len(embedded_chunks)
    total_dimension = 0

    for ec in embedded_chunks:
        dimension = len(ec.vector)
        total_dimension += dimension
        first_10 = ec.vector[:10]
        
        print("==================================================")
        print()
        print(f"Chunk Number: {ec.chunk_number}")
        print(f"Page Number: {ec.page}")
        print(f"Character Count: {len(ec.text)}")
        print(f"Text Preview (first 150 characters): {ec.text[:150]}")
        print()
        print(f"Vector Dimension: {dimension}")
        print()
        print(f"First 10 Values of the Vector: {first_10}")
        print()
    print("==================================================")

    # Calculate model and average dimension
    # default model name is BAAI/bge-small-en-v1.5
    model_name = "BAAI/bge-small-en-v1.5"
    avg_dimension = total_dimension / total_chunks if total_chunks > 0 else 0

    print(f"\nTotal Chunks: {total_chunks}")
    print(f"Embedding Model: {model_name}")
    print(f"Average Vector Dimension: {avg_dimension}")

if __name__ == "__main__":
    main()
