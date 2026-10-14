from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=32_000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=100)
    model: str | None = Field(default=None, description="Overrides OLLAMA_MODEL when set")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class ChatResponse(BaseModel):
    model: str
    message: ChatMessage


class HealthResponse(BaseModel):
    status: Literal["ok"]
    llm_reachable: bool
    model: str
    model_available: bool
