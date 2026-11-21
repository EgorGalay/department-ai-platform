from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    organization_id: UUID
    conversation_id: UUID | None = None
    message: str = Field(min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    conversation_id: UUID
    answer: str
