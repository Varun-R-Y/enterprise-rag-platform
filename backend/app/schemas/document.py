from datetime import datetime
from pydantic import BaseModel, UUID4
from app.models.document import DocumentStatus

class DocumentUploadResponse(BaseModel):
    document_id: UUID4
    message: str

class PageContent(BaseModel):
    page: int
    text: str


class Chunk(BaseModel):
    document_id: UUID4
    page: int
    chunk_number: int
    text: str


class EmbeddedChunk(BaseModel):
    tenant_id: UUID4
    document_id: UUID4
    page: int
    chunk_number: int
    text: str
    vector: list[float]
    uploaded_by: UUID4 | None = None


class RetrieveResult(BaseModel):
    score: float
    tenant_id: UUID4
    document_id: UUID4
    title: str
    original_filename: str
    page: int
    chunk_number: int
    text: str
    uploaded_by: UUID4 | None = None


class DocumentSummary(BaseModel):
    id: UUID4
    original_filename: str
    status: DocumentStatus
    uploaded_at: datetime
    chunk_count: int
    file_size: int



