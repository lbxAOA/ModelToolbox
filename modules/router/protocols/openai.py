"""Strict text-only OpenAI chat-completions protocol adaptation."""

from __future__ import annotations

from typing import Any

from modules.foundation.errors import ValidationError
from modules.router.model import Exchange, Message, validate_exchange

_ALLOWED = {"model", "max_tokens", "messages", "stream"}


def parse_request(data: object) -> Exchange:
    if not isinstance(data, dict) or set(data) - _ALLOWED:
        raise ValidationError("unsupported-router-request", "Router request fields are not supported.")
    if data.get("stream", False):
        raise ValidationError("unsupported-router-stream", "Streaming is not enabled yet.")
    raw_messages = data.get("messages")
    if not isinstance(raw_messages, list):
        raise ValidationError("invalid-router-messages", "Router messages are required.")
    messages: list[Message] = []
    for item in raw_messages:
        if not isinstance(item, dict) or set(item) != {"role", "content"} or not isinstance(item.get("content"), str):
            raise ValidationError("unsupported-router-content", "Router supports only text messages.")
        messages.append(Message(item["role"], item["content"]))
    return validate_exchange(data.get("model"), data.get("max_tokens"), messages)


def render_request(exchange: Exchange) -> dict[str, Any]:
    return {"model": exchange.model, "max_tokens": exchange.max_tokens, "messages": [{"role": item.role, "content": item.text} for item in exchange.messages]}


def render_response(data: object) -> dict[str, Any]:
    if not isinstance(data, dict) or not isinstance(data.get("choices"), list) or not data["choices"]:
        raise ValidationError("invalid-upstream-response", "Upstream response format is unsupported.")
    choice = data["choices"][0]
    if not isinstance(choice, dict) or not isinstance(choice.get("message"), dict) or not isinstance(choice["message"].get("content"), str):
        raise ValidationError("invalid-upstream-response", "Upstream response did not contain text.")
    return {"text": choice["message"]["content"], "model": data.get("model") if isinstance(data.get("model"), str) else None}
