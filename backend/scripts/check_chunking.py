import sys
import uuid
from pathlib import Path

# Ensure app modules can be imported
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.services.pdf_service import PDFService
from app.services.chunking_service import ChunkingService

def main():
    # 1. Locate the sample PDF in the uploads folder
    uploads_dir = Path("uploads")
    pdf_files = list(uploads_dir.glob("**/*.pdf"))
    
    if not pdf_files:
        print("Error: No sample PDF found in the uploads/ directory.")
        print("Please upload a PDF or place one in the uploads/ directory first.")
        return

    sample_pdf = pdf_files[0]
    print(f"Loading sample PDF: {sample_pdf}\n")

    # 2. Extract text using PDFService
    pdf_service = PDFService()
    try:
        pages = pdf_service.extract_text(sample_pdf)
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return

    # 3. Use ChunkingService to generate chunks
    chunking_service = ChunkingService(chunk_size=800, chunk_overlap=150)
    document_id = uuid.uuid4()
    chunks = chunking_service.chunk_document(document_id=document_id, pages=pages)

    print(f"Generated {len(chunks)} chunks total.")

    # 4. Print the first 4 chunks
    print("\n-----------------------------------")
    for chunk in chunks[:4]:
        print(f"Chunk Number: {chunk.chunk_number}")
        print(f"Page Number: {chunk.page}")
        print(f"Character Count: {len(chunk.text)}")
        print(f"Chunk Text:\n{chunk.text}")
        print("-----------------------------------")

if __name__ == "__main__":
    main()
