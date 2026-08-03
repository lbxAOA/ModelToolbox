from __future__ import annotations

import os

from .base import ProviderConfig
from .http import request_json
from modeltoolbox_provider.types import (
    ChatMessage,
    ChatResult,
    EmbeddingResult,
    ModelInfo,
    ProviderCapabilities,
    ProviderError,
)


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, config: ProviderConfig) -> None:
        self.base_url = (
            config.base_url
            or os.environ.get("ANTHROPIC_BASE_URL")
            or "https://api.anthropic.com/v1"
        ).rstrip("/")
        self.api_key = config.api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.default_model = config.model
        self.timeout = config.timeout

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            name=self.name,
            chat=True,
            embed=False,
            models=True,
        )

    def _headers(self) -> dict[str, str]:
        headers = {"anthropic-version": "2023-06-01"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def models(self) -> list[ModelInfo]:
        payload = request_json(
            "GET",
            f"{self.base_url}/models",
            headers=self._headers(),
            timeout=self.timeout,
        )
        data = payload.get("data", [])
        if not isinstance(data, list):
            raise ProviderError("Anthropic returned an invalid models payload")
        return [
            ModelInfo(
                name=str(item.get("id", "")),
                provider=self.name,
                capabilities=("chat",),
                metadata=item,
            )
            for item in data
            if isinstance(item, dict) and item.get("id")
        ]

    def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
    ) -> ChatResult:
        selected_model = model or self.default_model
        if not selected_model:
            raise ProviderError("Anthropic chat requires --model or provider.model in config")
        system = "\n".join(message.content for message in messages if message.role == "system")
        user_messages = [
            {"role": message.role, "content": message.content}
            for message in messages
            if message.role in {"user", "assistant"}
        ]
        payload = {
            "model": selected_model,
            "max_tokens": 4096,
            "messages": user_messages,
        }
        if system:
            payload["system"] = system
        response = request_json(
            "POST",
            f"{self.base_url}/messages",
            headers=self._headers(),
            payload=payload,
            timeout=self.timeout,
        )
        content = response.get("content", [])
        text = "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
        if not text:
            raise ProviderError("Anthropic returned an invalid chat payload")
        usage = response.get("usage") if isinstance(response.get("usage"), dict) else None
        return ChatResult(
            content=text,
            model=selected_model,
            provider=self.name,
            usage=usage,
            raw=response,
        )

    def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> list[EmbeddingResult]:
        raise ProviderError("Anthropic does not expose embeddings through this adapter")