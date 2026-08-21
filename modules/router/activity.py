"""Bounded redacted router activity records."""

from __future__ import annotations

import time
from collections import deque
from typing import Any


class ActivityLog:
    def __init__(self, limit: int = 64) -> None:
        self._events: deque[dict[str, Any]] = deque(maxlen=limit)

    def append(self, policy_revision: int, inbound: str, upstream: str, outcome: str, status: int | None, elapsed_ms: int) -> None:
        self._events.appendleft({"time": int(time.time()), "policy_revision": policy_revision, "inbound_protocol": inbound, "upstream_protocol": upstream, "outcome": outcome, "status": status, "elapsed_ms": elapsed_ms})

    def list(self) -> dict[str, Any]:
        return {"events": list(self._events)}
