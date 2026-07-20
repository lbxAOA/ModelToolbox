"""Anthropic Messages API 适配器。"""
from __future__ import annotations

from ..base import Provider
from ..http import post_json
from ..types import ChatRequest, ChatResponse, ImagePart, Message, TextPart, Usage

ANTHROPIC_VERSION = "2023-06-01"


def _content_parts(msg: Message) -> list[dict]:
    out: list[dict] = []
    for p in msg.parts():
        if isinstance(p, TextPart):
            out.append({"type": "text", "text": p.text})
        elif isinstance(p, ImagePart):
            out.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": p.mime,
                        "data": p.data,
                    },
                }
            )
    return out


class AnthropicProvider(Provider):
    def chat(self, request: ChatRequest) -> ChatResponse:
        cfg = self.config
        url = f"{cfg.base_url}/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": cfg.api_key or "",
            "anthropic-version": ANTHROPIC_VERSION,
        }
        # Anthropic 把 system 单独拎出，其余进 messages。
        system_txt = "\n".join(
            m.text() for m in request.messages if m.role == "system"
        )
        msgs = [
            {"role": m.role, "content": _content_parts(m)}
            for m in request.messages
            if m.role != "system"
        ]
        body: dict = {
            "model": request.model or cfg.model,
            "messages": msgs,
            "max_tokens": request.max_tokens or 1024,
            "temperature": request.temperature,
        }
        if system_txt:
            body["system"] = system_txt
        if request.stop:
            body["stop_sequences"] = request.stop
        body.update(request.extra)

        data = post_json(url, headers, body)
        blocks = data.get("content") or []
        text = "".join(
            b.get("text", "") for b in blocks if b.get("type") == "text"
        )
        u = data.get("usage") or {}
        usage = Usage(
            prompt_tokens=u.get("input_tokens", 0),
            completion_tokens=u.get("output_tokens", 0),
            total_tokens=u.get("input_tokens", 0) + u.get("output_tokens", 0),
        )
        return ChatResponse(
            text=text,
            model=data.get("model", body["model"]),
            provider=self.name,
            usage=usage,
            raw=data,
        )
