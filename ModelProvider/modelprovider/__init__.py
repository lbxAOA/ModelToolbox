"""ModelProvider — ModelToolbox 的统一大模型调用层。

把 OpenAI / Anthropic / Gemini / DeepSeek 及本地 Ollama 统一到一个接口，
服务三种角色：数据蒸馏老师(teacher)、兜底/对比(fallback)、训练前跑通(runner)。
"""
from __future__ import annotations

from .client import LLMClient
from .config import SPECS, ResolvedConfig, load_dotenv, resolve, resolve_role
from .types import (
    ChatRequest,
    ChatResponse,
    ImagePart,
    Message,
    TextPart,
    Usage,
)

__all__ = [
    "LLMClient",
    "Message",
    "TextPart",
    "ImagePart",
    "ChatRequest",
    "ChatResponse",
    "Usage",
    "SPECS",
    "ResolvedConfig",
    "resolve",
    "resolve_role",
    "load_dotenv",
]

__version__ = "0.1.0"
