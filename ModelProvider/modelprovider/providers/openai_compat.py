"""OpenAI 兼容协议适配器（OpenAI / DeepSeek / Ollama 共用）。"""
from __future__ import annotations

from ..base import Provider
from ..http import post_json
from ..types import ChatRequest, ChatResponse, ImagePart, Message, TextPart, Usage


def _message_to_dict(msg: Message) -> dict:
    parts = msg.parts()
    # 纯文本消息用简单字符串形式，兼容性最好。
    if len(parts) == 1 and isinstance(parts[0], TextPart):
        return {"role": msg.role, "content": parts[0].text}
    content: list[dict] = []
    for p in parts:
        if isinstance(p, TextPart):
            content.append({"type": "text", "text": p.text})
        elif isinstance(p, ImagePart):
            content.append(
                {"type": "image_url", "image_url": {"url": p.data_uri()}}
            )
    return {"role": msg.role, "content": content}


class OpenAICompatProvider(Provider):
    def chat(self, request: ChatRequest) -> ChatResponse:
        cfg = self.config
        url = f"{cfg.base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if cfg.api_key:
            headers["Authorization"] = f"Bearer {cfg.api_key}"
        body: dict = {
            "model": request.model or cfg.model,
            "messages": [_message_to_dict(m) for m in request.messages],
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            body["max_tokens"] = request.max_tokens
        if request.stop:
            body["stop"] = request.stop
        body.update(request.extra)

        data = post_json(url, headers, body)
        choice = (data.get("choices") or [{}])[0]
        text = (choice.get("message") or {}).get("content", "") or ""
        u = data.get("usage") or {}
        usage = Usage(
            prompt_tokens=u.get("prompt_tokens", 0),
            completion_tokens=u.get("completion_tokens", 0),
            total_tokens=u.get("total_tokens", 0),
        )
        return ChatResponse(
            text=text,
            model=data.get("model", body["model"]),
            provider=self.name,
            usage=usage,
            raw=data,
        )
