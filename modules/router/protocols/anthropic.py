"""Strict text-only Anthropic Messages protocol adaptation."""

from __future__ import annotations

from typing import Any

from modules.foundation.errors import ValidationError
from modules.router.model import Exchange, Message, validate_exchange

_ALLOWED = {"model", "max_tokens", "system", "messages", "stream"}


def parse_request(data: object) -> Exchange:
    if not isinstance(data, dict) or set(data) - _ALLOWED:
        raise ValidationError("unsupported-router-request", "Router request fields are not supported.")
    if data.get("stream", False):
        raise ValidationError("unsupported-router-stream", "Streaming is not enabled yet.")
    system = data.get("system")
    messages: list[Message] = []
    if system is not None:
        if not isinstance(system, str):
            raise ValidationError("unsupported-router-content", "Router supports only text system content.")
        messages.append(Message("system", system))
    raw_messages = data.get("messages")
    if not isinstance(raw_messages, list):
        raise ValidationError("invalid-router-messages", "Router messages are required.")
    for item in raw_messages:
        if not isinstance(item, dict) or set(item) != {"role", "content"} or not isinstance(item.get("content"), str):
            raise ValidationError("unsupported-router-content", "Router supports only text messages.")
        messages.append(Message(item["role"], item["content"]))
    return validate_exchange(data.get("model"), data.get("max_tokens"), messages)


def render_response(data: object) -> dict[str, Any]:
    if not isinstance(data, dict) or not isinstance(data.get("content"), list):
        raise ValidationError("invalid-upstream-response", "Upstream response format is unsupported.")
    text = "".join(block.get("text", "") for block in data["content"] if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str))
    if not text:
        raise ValidationError("invalid-upstream-response", "Upstream response did not contain text.")
    return {"text": text, "model": data.get("model") if isinstance(data.get("model"), str) else None}
