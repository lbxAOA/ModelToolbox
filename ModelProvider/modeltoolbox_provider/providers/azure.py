from __future__ import annotations

import os
from urllib.parse import urlencode

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


class AzureOpenAIProvider:
    name = "azure"

    def __init__(self, config: ProviderConfig) -> None:
        self.base_url = (
            config.base_url
            or os.environ.get("AZURE_OPENAI_ENDPOINT")
            or os.environ.get("AZURE_BASE_URL")
            or ""
        ).rstrip("/")
        self.api_key = (
            config.api_key
            or os.environ.get("AZURE_OPENAI_API_KEY")
            or os.environ.get("AZURE_API_KEY")
        )
        self.default_model = config.model
        self.timeout = config.timeout
        self.api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            name=self.name,
            chat=True,
            embed=True,
            models=False,
        )

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.api_key:
            headers["api-key"] = self.api_key
        return headers

    def _deployment_url(self, deployment: str, operation: str) -> str:
        if not self.base_url:
            raise ProviderError("Azure provider requires --base-url or AZURE_OPENAI_ENDPOINT")
        query = urlencode({"api-version": self.api_version})
        return f"{self.base_url}/openai/deployments/{deployment}/{operation}?{query}"

    def models(self) -> list[ModelInfo]:
        return []

    def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
    ) -> ChatResult:
        deployment = model or self.default_model
        if not deployment:
            raise ProviderError("Azure chat requires --model as deployment name")
        payload = request_json(
            "POST",
            self._deployment_url(deployment, "chat/completions"),
            headers=self._headers(),
            payload={
                "messages": [
                    {"role": message.role, "content": message.content}
                    for message in messages
                ]
            },
            timeout=self.timeout,
        )
        choices = payload.get("choices", [])
        first = choices[0] if isinstance(choices, list) and choices else None
        message = first.get("message") if isinstance(first, dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise ProviderError("Azure returned an invalid chat payload")
        usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else None
        return ChatResult(
            content=content,
            model=deployment,
            provider=self.name,
            usage=usage,
            raw=payload,
        )

    def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> list[EmbeddingResult]:
        deployment = model or self.default_model
        if not deployment:
            raise ProviderError("Azure embed requires --model as deployment name")
        payload = request_json(
            "POST",
            self._deployment_url(deployment, "embeddings"),
            headers=self._headers(),
            payload={"input": texts if len(texts) != 1 else texts[0]},
            timeout=self.timeout,
        )
        rows = payload.get("data", [])
        if not isinstance(rows, list):
            raise ProviderError("Azure returned an invalid embedding payload")
        return [
            EmbeddingResult(
                embedding=[float(value) for value in row["embedding"]],
                model=deployment,
                provider=self.name,
                raw=row,
            )
            for row in rows
            if isinstance(row, dict) and isinstance(row.get("embedding"), list)
        ]