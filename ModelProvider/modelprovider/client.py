"""高层客户端：一行代码调用任意 provider 或角色。"""
from __future__ import annotations

from typing import Optional, Union

from . import config
from .base import Provider, build
from .types import ChatRequest, ChatResponse, Message


class LLMClient:
    """统一入口。

    用法::

        from modelprovider import LLMClient
        client = LLMClient.for_provider("deepseek")
        print(client.ask("用一句话解释什么是运放"))

        teacher = LLMClient.for_role("teacher")   # 数据蒸馏老师
    """

    def __init__(self, provider: Provider):
        self.provider = provider

    # -- 构造 --------------------------------------------------------------
    @classmethod
    def for_provider(
        cls, provider: str, model: Optional[str] = None, load_env: bool = True
    ) -> "LLMClient":
        if load_env:
            config.load_dotenv()
        return cls(build(config.resolve(provider, model)))

    @classmethod
    def for_role(cls, role: str, load_env: bool = True) -> "LLMClient":
        if load_env:
            config.load_dotenv()
        return cls(build(config.resolve_role(role)))

    # -- 调用 --------------------------------------------------------------
    def chat(self, request: ChatRequest) -> ChatResponse:
        return self.provider.chat(request)

    def ask(
        self,
        prompt: Union[str, list[Message]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """便捷方法：传字符串或 Message 列表，返回纯文本回答。"""
        if isinstance(prompt, str):
            messages = [Message.user(prompt)]
        else:
            messages = list(prompt)
        if system:
            messages = [Message.system(system), *messages]
        req = ChatRequest(
            messages=messages, temperature=temperature, max_tokens=max_tokens
        )
        return self.chat(req).text

    def ping(self) -> bool:
        return self.provider.ping()

    @property
    def name(self) -> str:
        return self.provider.name
