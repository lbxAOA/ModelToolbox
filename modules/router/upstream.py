"""Bounded upstream forwarding that never persists request or response content."""

from __future__ import annotations

import http.client
import json
from typing import Any
from urllib.parse import urlparse

from modules.foundation.errors import ValidationError

_MAX_RESPONSE = 1_000_000


def forward(url: str, path: str, payload: dict[str, Any], authorization: str | None) -> tuple[int, object]:
    parsed = urlparse(url)
    connection_type = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    connection = connection_type(parsed.hostname, parsed.port, timeout=10)
    base_path = parsed.path.rstrip("/")
    if base_path.endswith("/v1") and path.startswith("/v1/"):
        target = base_path + path[3:]
    else:
        target = (base_path + path) or path
    headers = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "ModelToolbox-LocalRouter/0.1"}
    if authorization is not None:
        headers["Authorization"] = authorization
    try:
        connection.request("POST", target, body=json.dumps(payload, separators=(",", ":")).encode("utf-8"), headers=headers)
        response = connection.getresponse()
        raw = response.read(_MAX_RESPONSE + 1)
    except (OSError, http.client.HTTPException) as error:
        raise ValidationError("upstream-unavailable", "Upstream service could not be reached.") from error
    finally:
        connection.close()
    if len(raw) > _MAX_RESPONSE:
        raise ValidationError("upstream-response-too-large", "Upstream response exceeded the router limit.")
    try:
        return response.status, json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValidationError("invalid-upstream-response", "Upstream response was not valid JSON.") from error
