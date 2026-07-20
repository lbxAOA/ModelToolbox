"""统一的请求/响应数据模型（provider 无关）。

设计目标：以 OpenAI Chat Completions 的 message 结构作为中立基准，
各 provider 适配器负责把它翻译成自己家的协议。支持多模态（文本 + 图像）。
"""
from __future__ import annotations

import base64
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional, Union

Role = Literal["system", "user", "assistant"]


@dataclass
class TextPart:
    """一段文本内容。"""

    text: str
    type: Literal["text"] = "text"


@dataclass
class ImagePart:
    """一张图像内容（base64 内联）。

    统一以 base64 + mime 持有，适配器再翻译成各家格式：
    - OpenAI 兼容: image_url -> data URI
    - Anthropic:   source.type=base64
    - Gemini:      inlineData
    """

    data: str  # base64（不含 data URI 前缀）
    mime: str = "image/png"
    type: Literal["image"] = "image"

    @classmethod
    def from_path(cls, path: Union[str, Path]) -> "ImagePart":
        p = Path(path)
        mime, _ = mimetypes.guess_type(p.name)
        data = base64.b64encode(p.read_bytes()).decode("ascii")
        return cls(data=data, mime=mime or "image/png")

    @classmethod
    def from_bytes(cls, raw: bytes, mime: str = "image/png") -> "ImagePart":
        return cls(data=base64.b64encode(raw).decode("ascii"), mime=mime)

    def data_uri(self) -> str:
        return f"data:{self.mime};base64,{self.data}"


ContentPart = Union[TextPart, ImagePart]


@dataclass
class Message:
    """一条对话消息。content 可为纯文本或多模态分片列表。"""

    role: Role
    content: Union[str, list[ContentPart]]

    @classmethod
    def system(cls, text: str) -> "Message":
        return cls("system", text)

    @classmethod
    def user(cls, text: str) -> "Message":
        return cls("user", text)

    @classmethod
    def assistant(cls, text: str) -> "Message":
        return cls("assistant", text)

    def parts(self) -> list[ContentPart]:
        """始终以分片列表形式返回内容，便于适配器统一处理。"""
        if isinstance(self.content, str):
            return [TextPart(self.content)]
        return list(self.content)

    def text(self) -> str:
        """把内容压平成纯文本（丢弃图像），便于日志/回退。"""
        return "".join(p.text for p in self.parts() if isinstance(p, TextPart))


@dataclass
class ChatRequest:
    messages: list[Message]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stop: Optional[list[str]] = None
    extra: dict = field(default_factory=dict)


@dataclass
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class ChatResponse:
    text: str
    model: str
    provider: str
    usage: Usage = field(default_factory=Usage)
    raw: dict = field(default_factory=dict)
