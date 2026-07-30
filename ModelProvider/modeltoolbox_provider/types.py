from __future__ import annotations

from dataclasses import dataclass
from typing import Any, AsyncIterator, Literal


Role = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True)
class ChatMessage:
    role: Role
    content: str
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema


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
    finish_reason: str | None = None


@dataclass(frozen=True)
class StreamChunk:
    """流式响应的单个片段"""
    content: str
    finish_reason: str | None = None
    model: str | None = None
    usage: dict[str, Any] | None = None


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
    stream: bool = False  # 支持流式聊天
    tools: bool = False   # 支持工具调用
    local: bool = False


class ProviderError(RuntimeError):
    """Provider 操作失败的基础异常"""
    pass


class StreamError(ProviderError):
    """流式传输错误"""
    pass


class ToolCallError(ProviderError):
    """工具调用错误"""
    pass