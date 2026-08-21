"""Normalized text-only exchanges for the first router milestone."""

from __future__ import annotations

from dataclasses import dataclass

from modules.foundation.errors import ValidationError


@dataclass(frozen=True)
class Message:
    role: str
    text: str


@dataclass(frozen=True)
class Exchange:
    model: str
    max_tokens: int
    messages: tuple[Message, ...]


def validate_exchange(model: object, max_tokens: object, messages: object) -> Exchange:
    if not isinstance(model, str) or not model or len(model) > 160:
        raise ValidationError("invalid-router-model", "Router model is invalid.")
    if not isinstance(max_tokens, int) or not 1 <= max_tokens <= 16_384:
        raise ValidationError("invalid-router-max-tokens", "Router max tokens is invalid.")
    if not isinstance(messages, (list, tuple)) or not messages or len(messages) > 128:
        raise ValidationError("invalid-router-messages", "Router requires one to 128 text messages.")
    normalized: list[Message] = []
    for item in messages:
        if not isinstance(item, Message) or item.role not in {"system", "user", "assistant"} or not item.text or len(item.text) > 200_000:
            raise ValidationError("unsupported-router-content", "Router supports only bounded non-empty text messages.")
        normalized.append(item)
    return Exchange(model, max_tokens, tuple(normalized))
