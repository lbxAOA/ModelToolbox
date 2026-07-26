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


class OllamaProvider:
    name = "ollama"

    def __init__(self, config: ProviderConfig) -> None:
        self.base_url = (
            config.base_url
            or os.environ.get("OLLAMA_HOST")
            or "http://127.0.0.1:11434"
        ).rstrip("/")
        self.default_model = config.model
        self.timeout = config.timeout

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            name=self.name,
            chat=True,
            embed=True,
            models=True,
            local=True,
        )

    def models(self) -> list[ModelInfo]:
        payload = request_json(
            "GET",
            f"{self.base_url}/api/tags",
            timeout=self.timeout,
        )
        models = payload.get("models", [])
        if not isinstance(models, list):
            raise ProviderError("Ollama returned an invalid models payload")
        return [
            ModelInfo(
                name=str(item.get("name", "")),
                provider=self.name,
                capabilities=("chat", "embed"),
                metadata=item if isinstance(item, dict) else None,
            )
            for item in models
            if isinstance(item, dict) and item.get("name")
        ]

    def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
    ) -> ChatResult:
        selected_model = model or self.default_model
        if not selected_model:
            raise ProviderError(
                "Ollama chat requires --model or provider.model in config"
            )
        payload = request_json(
            "POST",
            f"{self.base_url}/api/chat",
            payload={
                "model": selected_model,
                "messages": [
                    {"role": message.role, "content": message.content}
                    for message in messages
                ],
                "stream": False,
            },
            timeout=self.timeout,
        )
        message = payload.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise ProviderError("Ollama returned an invalid chat payload")
        return ChatResult(
            content=content,
            model=selected_model,
            provider=self.name,
            raw=payload,
        )

    def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> list[EmbeddingResult]:
        selected_model = model or self.default_model
        if not selected_model:
            raise ProviderError(
                "Ollama embed requires --model or provider.model in config"
            )
        payload = request_json(
            "POST",
            f"{self.base_url}/api/embed",
            payload={"model": selected_model, "input": texts},
            timeout=self.timeout,
        )
        embeddings = payload.get("embeddings")
        if not isinstance(embeddings, list):
            single = payload.get("embedding")
            embeddings = [single] if isinstance(single, list) else None
        if not isinstance(embeddings, list):
            raise ProviderError("Ollama returned an invalid embedding payload")
        return [
            EmbeddingResult(
                embedding=[float(value) for value in embedding],
                model=selected_model,
                provider=self.name,
                raw=payload,
            )
            for embedding in embeddings
            if isinstance(embedding, list)
        ]