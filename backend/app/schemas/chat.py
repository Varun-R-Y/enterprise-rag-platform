from pydantic import BaseModel, Field


class Source(BaseModel):
    """
    Metadata representation of a retrieved document chunk used in LLM generation.
    """
    document: str
    page: int
    score: float


class ChatResponse(BaseModel):
    """
    Response object returned from ChatService orchestration containing LLM answer and citations.
    """
    answer: str
    sources: list[Source] = Field(default_factory=list)
