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


class OpenAICompatibleProvider:
    name = "openai-compatible"

    def __init__(self, config: ProviderConfig) -> None:
        env_prefix = (
            "OPENAI"
            if config.name in {"openai", "openai-compatible"}
            else config.name.upper()
        )
        self.provider_name = config.name
        self.base_url = (
            config.base_url
            or os.environ.get(f"{env_prefix}_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        self.api_key = (
            config.api_key
            or os.environ.get(f"{env_prefix}_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        )
        self.default_model = config.model
        self.timeout = config.timeout

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            name=self.provider_name,
            chat=True,
            embed=True,
            models=True,
            local=False,
        )

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
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
            raise ProviderError("Provider returned an invalid models payload")
        return [
            ModelInfo(
                name=str(item.get("id", "")),
                provider=self.provider_name,
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
            raise ProviderError("Chat requires --model or provider.model in config")
        payload = request_json(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            payload={
                "model": selected_model,
                "messages": [
                    {"role": message.role, "content": message.content}
                    for message in messages
                ],
            },
            timeout=self.timeout,
        )
        choices = payload.get("choices", [])
        first = choices[0] if isinstance(choices, list) and choices else None
        message = first.get("message") if isinstance(first, dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise ProviderError("Provider returned an invalid chat payload")
        usage = (
            payload.get("usage")
            if isinstance(payload.get("usage"), dict)
            else None
        )
        return ChatResult(
            content=content,
            model=selected_model,
            provider=self.provider_name,
            usage=usage,
            raw=payload,
        )

    def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> list[EmbeddingResult]:
        selected_model = model or self.default_model
        if not selected_model:
            raise ProviderError("Embedding requires --model or provider.model in config")
        payload = request_json(
            "POST",
            f"{self.base_url}/embeddings",
            headers=self._headers(),
            payload={
                "model": selected_model,
                "input": texts if len(texts) != 1 else texts[0],
            },
            timeout=self.timeout,
        )
        rows = payload.get("data", [])
        if not isinstance(rows, list):
            raise ProviderError("Provider returned an invalid embedding payload")
        return [
            EmbeddingResult(
                embedding=[float(value) for value in row["embedding"]],
                model=selected_model,
                provider=self.provider_name,
                raw=row,
            )
            for row in rows
            if isinstance(row, dict) and isinstance(row.get("embedding"), list)
        ]