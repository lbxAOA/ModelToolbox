"""Provider 抽象基类与注册表。"""
from __future__ import annotations

from abc import ABC, abstractmethod

from .config import ResolvedConfig
from .types import ChatRequest, ChatResponse


class Provider(ABC):
    """所有 provider 适配器的统一接口。"""

    def __init__(self, config: ResolvedConfig):
        self.config = config

    @property
    def name(self) -> str:
        return self.config.spec.name

    @abstractmethod
    def chat(self, request: ChatRequest) -> ChatResponse:
        """执行一次对话补全。"""

    def ping(self) -> bool:
        """轻量连通性检查（默认发一句最小请求）。"""
        from .types import Message

        req = ChatRequest(messages=[Message.user("ping")], max_tokens=1)
        self.chat(req)
        return True


def build(config: ResolvedConfig) -> Provider:
    """按 spec.kind 构造具体 provider。"""
    kind = config.spec.kind
    if kind == "openai_compat":
        from .providers.openai_compat import OpenAICompatProvider

        return OpenAICompatProvider(config)
    if kind == "anthropic":
        from .providers.anthropic import AnthropicProvider

        return AnthropicProvider(config)
    if kind == "gemini":
        from .providers.gemini import GeminiProvider

        return GeminiProvider(config)
    if kind == "cli_agent":
        from .providers.cli_agent import CLIAgentProvider

        return CLIAgentProvider(config)
    raise ValueError(f"未支持的 provider kind: {kind!r}")
