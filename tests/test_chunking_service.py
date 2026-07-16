import uuid
import pytest
from app.schemas.document import PageContent, Chunk
from app.services.chunking_service import ChunkingService

def test_chunking_service_basic():
    # Arrange
    service = ChunkingService(chunk_size=50, chunk_overlap=10)
    doc_id = uuid.uuid4()
    pages = [
        PageContent(
            page=1,
            text="This is a test of the chunking service. It splits long text."
        ),
        PageContent(
            page=2,
            text="Here is another page of text that needs to be split."
        )
    ]

    # Act
    chunks = service.chunk_document(document_id=doc_id, pages=pages)

    # Assert
    assert len(chunks) > 0
    assert all(isinstance(c, Chunk) for c in chunks)
    assert all(c.document_id == doc_id for c in chunks)
    
    # Check sequential numbering starting from 0
    for idx, chunk in enumerate(chunks):
        assert chunk.chunk_number == idx

    # Check page preservation
    # The first chunk should correspond to page 1
    assert chunks[0].page == 1
    # The last chunk should correspond to page 2
    assert chunks[-1].page == 2

def test_chunking_service_empty_and_whitespace():
    # Arrange
    service = ChunkingService(chunk_size=100, chunk_overlap=10)
    doc_id = uuid.uuid4()
    pages = [
        PageContent(page=1, text="   Some text with leading and trailing space.   "),
        PageContent(page=2, text="      "), # Whitespace only
        PageContent(page=3, text=""),       # Empty string
        PageContent(page=4, text="Valid text on page 4")
    ]

    # Act
    chunks = service.chunk_document(document_id=doc_id, pages=pages)

    # Assert
    # We should have chunks for page 1 and page 4. Page 2 and 3 should be ignored.
    assert len(chunks) == 2
    
    # Page 1 checks
    assert chunks[0].page == 1
    assert chunks[0].chunk_number == 0
    assert chunks[0].text == "Some text with leading and trailing space."

    # Page 4 checks
    assert chunks[1].page == 4
    assert chunks[1].chunk_number == 1
    assert chunks[1].text == "Valid text on page 4"

def test_chunking_service_empty_pages_list():
    # Arrange
    service = ChunkingService()
    doc_id = uuid.uuid4()
    
    # Act
    chunks = service.chunk_document(document_id=doc_id, pages=[])

    # Assert
    assert chunks == []
