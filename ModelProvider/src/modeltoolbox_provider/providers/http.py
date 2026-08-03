from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from modeltoolbox_provider.types import ProviderError


def request_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
    timeout: float = 60.0,
) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, method=method.upper())
    request.add_header("Accept", "application/json")
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        request.add_header(key, value)

    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ProviderError(f"HTTP {exc.code} from {url}: {detail}") from exc
    except URLError as exc:
        raise ProviderError(f"Cannot reach {url}: {exc.reason}") from exc

    if not raw.strip():
        return {}
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProviderError(f"Invalid JSON from {url}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ProviderError(f"Expected JSON object from {url}")
    return loaded