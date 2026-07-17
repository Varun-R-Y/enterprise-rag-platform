from pydantic import BaseModel, UUID4

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


class RetrieveResult(BaseModel):
    score: float
    tenant_id: UUID4
    document_id: UUID4
    title: str
    original_filename: str
    page: int
    chunk_number: int
    text: str



