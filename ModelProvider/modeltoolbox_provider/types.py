from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


Role = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True)
class ChatMessage:
    role: Role
    content: str


@dataclass(frozen=True)
class ModelInfo:
    name: str
    provider: str
    capabilities: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class ChatResult:
    content: str
    model: str
    provider: str
    usage: dict[str, Any] | None = None
    raw: dict[str, Any] | None = None


@dataclass(frozen=True)
class EmbeddingResult:
    embedding: list[float]
    model: str
    provider: str
    raw: dict[str, Any] | None = None


@dataclass(frozen=True)
class ProviderCapabilities:
    name: str
    chat: bool
    embed: bool
    models: bool
    local: bool = False


class ProviderError(RuntimeError):
    pass