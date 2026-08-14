"""Structured local logging with conservative secret redaction."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import TextIO

_SECRET_PARTS = ("password", "secret", "token", "key")


class Logger:
    def __init__(self, stream: TextIO, minimum_level: str = "info") -> None:
        self._stream = stream
        self._minimum_level = minimum_level

    def log(self, level: str, event: str, **fields: object) -> None:
        levels = {"debug": 10, "info": 20, "warning": 30, "error": 40}
        if levels[level] < levels[self._minimum_level]:
            return
        safe_fields = {
            name: "[redacted]" if any(part in name.lower() for part in _SECRET_PARTS) else value
            for name, value in fields.items()
        }
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": level,
            "event": event,
            "fields": safe_fields,
        }
        self._stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        self._stream.flush()
