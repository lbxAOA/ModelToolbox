from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterator, Protocol

from modeltoolbox_provider.types import (
    ChatMessage,
    ChatResult,
    EmbeddingResult,
    ModelInfo,
    ProviderCapabilities,
    StreamChunk,
    ToolDefinition,
)


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    base_url: str | None = None
    api_key: str | None = None
    model: str | None = None
    timeout: float = 60.0
    max_retries: int = 3


class Provider(Protocol):
    name: str

    def capabilities(self) -> ProviderCapabilities:
        ...

    def models(self) -> list[ModelInfo]:
        ...

    def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> ChatResult:
        ...

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[StreamChunk]:
        ...

    def embed(self, texts: list[str], model: str | None = None) -> list[EmbeddingResult]:
        ...


def provider_names() -> tuple[str, ...]:
    return ("ollama", "openai-compatible", "anthropic", "azure")


def create_provider(config: ProviderConfig) -> Provider:
    if config.name == "ollama":
        from .ollama import OllamaProvider

        return OllamaProvider(config)
    if config.name in {"openai", "openai-compatible"}:
        from .openai_compatible import OpenAICompatibleProvider

        return OpenAICompatibleProvider(config)
    if config.name == "anthropic":
        from .anthropic import AnthropicProvider

        return AnthropicProvider(config)
    if config.name == "azure":
        from .azure import AzureOpenAIProvider

        return AzureOpenAIProvider(config)
    raise ValueError(f"Unknown provider: {config.name}")