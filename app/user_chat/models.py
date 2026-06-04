"""Pydantic models for user chat requests and responses."""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"
    conversation_id: str = "default"


class ChatResponse(BaseModel):
    message: str
    user_id: str
    conversation_id: str
    history: list[ChatMessage] = Field(default_factory=list)
