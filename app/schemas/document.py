from pydantic import BaseModel, UUID4

class DocumentUploadResponse(BaseModel):
    document_id: UUID4
    message: str

class PageContent(BaseModel):
    page: int
    text: str

