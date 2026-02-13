from pydantic import Field
from beanie import Document

from .utils import noid


class Agent(Document):
    "AI Agent"

    id: str = Field(default_factory=noid)
    prompt: str
    temperature: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    max_tokens: int | None = None
