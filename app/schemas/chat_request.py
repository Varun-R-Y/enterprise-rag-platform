from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Request payload schema for Chat API.
    """
    question: str
    top_k: int = Field(default=5)
    score_threshold: float | None = Field(default=None)
