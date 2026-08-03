from __future__ import annotations

import json
import os
from typing import AsyncIterator

import httpx

from .base import ProviderConfig
from modeltoolbox_provider.types import (
    ChatMessage,
    ChatResult,
    EmbeddingResult,
    ModelInfo,
    ProviderCapabilities,
    ProviderError,
    StreamChunk,
    StreamError,
    ToolDefinition,
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
        self._client = httpx.Client(timeout=self.timeout)
        self._async_client = httpx.AsyncClient(timeout=self.timeout)

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            name=self.name,
            chat=True,
            embed=True,
            models=True,
            stream=True,  # Ollama 支持流式
            tools=False,  # 暂不支持工具调用
            local=True,
        )

    def models(self) -> list[ModelInfo]:
        try:
            resp = self._client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            payload = resp.json()
        except httpx.HTTPError as e:
            raise ProviderError(f"Failed to list Ollama models: {e}")

        models = payload.get("models", [])
        if not isinstance(models, list):
            raise ProviderError("Ollama returned an invalid models payload")
        return [
            ModelInfo(
                name=str(item.get("name", "")),
                provider=self.name,
                capabilities=("chat", "embed", "stream"),
                metadata=item if isinstance(item, dict) else None,
            )
            for item in models
            if isinstance(item, dict) and item.get("name")
        ]

    def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> ChatResult:
        selected_model = model or self.default_model
        if not selected_model:
            raise ProviderError(
                "Ollama chat requires --model or provider.model in config"
            )

        payload = {
            "model": selected_model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            resp = self._client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            raise ProviderError(f"Ollama chat failed: {e}")

        message = data.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise ProviderError("Ollama returned an invalid chat payload")

        return ChatResult(
            content=content,
            model=selected_model,
            provider=self.name,
            usage={
                "prompt_tokens": data.get("prompt_eval_count"),
                "completion_tokens": data.get("eval_count"),
                "total_tokens": (data.get("prompt_eval_count", 0) + data.get("eval_count", 0)),
            },
            raw=data,
            finish_reason=data.get("done_reason"),
        )

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """流式聊天补全"""
        selected_model = model or self.default_model
        if not selected_model:
            raise ProviderError(
                "Ollama chat requires --model or provider.model in config"
            )

        payload = {
            "model": selected_model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
            "stream": True,
            "options": {
                "temperature": temperature,
            },
        }

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            async with self._async_client.stream(
                "POST", f"{self.base_url}/api/chat", json=payload
            ) as resp:
                resp.raise_for_status()

                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)

                        message = data.get("message", {})
                        content = message.get("content", "")
                        done = data.get("done", False)

                        chunk = StreamChunk(
                            content=content,
                            finish_reason="stop" if done else None,
                            model=selected_model,
                            usage={
                                "prompt_tokens": data.get("prompt_eval_count"),
                                "completion_tokens": data.get("eval_count"),
                            }
                            if done
                            else None,
                        )

                        yield chunk

                        if done:
                            break

                    except json.JSONDecodeError as e:
                        raise StreamError(f"Failed to parse stream chunk: {e}")

        except httpx.HTTPError as e:
            raise StreamError(f"Ollama stream failed: {e}")

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

        results = []
        for text in texts:
            payload = {
                "model": selected_model,
                "prompt": text,
            }

            try:
                resp = self._client.post(f"{self.base_url}/api/embeddings", json=payload)
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as e:
                raise ProviderError(f"Ollama embedding failed: {e}")

            embedding = data.get("embedding")
            if not isinstance(embedding, list):
                raise ProviderError("Ollama returned an invalid embedding payload")

            results.append(
                EmbeddingResult(
                    embedding=[float(value) for value in embedding],
                    model=selected_model,
                    provider=self.name,
                    raw=data,
                )
            )

        return results

    def __del__(self):
        """清理 HTTP 客户端"""
        try:
            self._client.close()
        except Exception:
            pass