from typing import Literal
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class RouteChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class SuggestedAction(BaseModel):
    type: Literal["create_stop", "create_route", "assign_driver", "optimize_route", "none"]
    label: str
    target_path: str | None = None


class RouteChatResponse(BaseModel):
    reply: str
    suggested_action: SuggestedAction
    provider: Literal["ollama", "openrouter", "stub"]
