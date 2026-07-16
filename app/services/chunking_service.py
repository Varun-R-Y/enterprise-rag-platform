import logging
from pydantic import UUID4
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.schemas.document import PageContent, Chunk

logger = logging.getLogger(__name__)

class ChunkingService:
    """
    Service to handle document chunking using RecursiveCharacterTextSplitter.
    Splits text while preserving page numbers and generating sequential chunk numbers.
    """

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

    def chunk_document(self, document_id: UUID4, pages: list[PageContent]) -> list[Chunk]:
        """
        Chunks a list of PageContent into a list of Chunk models.
        
        Args:
            document_id: The UUID of the document.
            pages: List of PageContent representing the document's pages.
            
        Returns:
            A list of Chunk objects.
        """
        chunks = []
        chunk_counter = 0

        for page_content in pages:
            # Skip page if text is empty or None
            if not page_content.text:
                continue

            # Split the page text
            split_texts = self.splitter.split_text(page_content.text)

            for raw_text in split_texts:
                # Strip unnecessary whitespace
                cleaned_text = raw_text.strip()
                
                # Ignore empty chunks
                if not cleaned_text:
                    continue

                # Create the Chunk object
                chunk = Chunk(
                    document_id=document_id,
                    page=page_content.page,
                    chunk_number=chunk_counter,
                    text=cleaned_text,
                )
                chunks.append(chunk)
                chunk_counter += 1

        logger.info(
            f"Successfully split document {document_id} into {len(chunks)} chunks."
        )
        return chunks


if __name__ == "__main__":
    import uuid

    # Setup basic logging
    logging.basicConfig(level=logging.INFO)

    # Example usage:
    # 1. Initialize the service
    chunking_service = ChunkingService(chunk_size=800, chunk_overlap=150)

    # 2. Mock some sample document data
    sample_doc_id = uuid.uuid4()
    sample_pages = [
        PageContent(
            page=1,
            text="   FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints.   \n\n   It has key features like speed, fast code writing, fewer bugs, and intuitive design.   "
        ),
        PageContent(
            page=2,
            text="   In this page we talk about LangChain. LangChain is a framework for developing applications powered by large language models (LLMs).   "
        ),
        PageContent(
            page=3,
            text="      " # Empty page to test ignoring empty chunks
        )
    ]

    # 3. Perform chunking
    result_chunks = chunking_service.chunk_document(document_id=sample_doc_id, pages=sample_pages)

    # 4. Display results
    print(f"\nCreated {len(result_chunks)} chunks for document {sample_doc_id}:\n")
    for c in result_chunks:
        print(f"Chunk #{c.chunk_number} (Page {c.page}):")
        print(f"Text: {repr(c.text)}")
        print("-" * 40)
