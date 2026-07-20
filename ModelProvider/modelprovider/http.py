"""极简 HTTP 传输层。

- 默认用标准库 urllib（零运行时依赖），可离线在测试中注入替身。
- 通过全局可替换的 `TRANSPORT` 实现依赖注入：测试里换成假函数即可，
  provider 代码无需感知网络。
"""
from __future__ import annotations

import json as _json
import urllib.error
import urllib.request
from typing import Callable, Optional

# 传输签名: (method, url, headers, json_body, timeout) -> (status_code, response_dict)
Transport = Callable[[str, str, dict, Optional[dict], float], "tuple[int, dict]"]


class HTTPError(RuntimeError):
    def __init__(self, status: int, body: str, url: str):
        super().__init__(f"HTTP {status} from {url}: {body[:500]}")
        self.status = status
        self.body = body
        self.url = url


def _urllib_transport(
    method: str, url: str, headers: dict, json_body: Optional[dict], timeout: float
) -> "tuple[int, dict]":
    data = None
    if json_body is not None:
        data = _json.dumps(json_body).encode("utf-8")
    req = urllib.request.Request(url=url, data=data, method=method)
    for k, v in headers.items():
        req.add_header(k, v)
    if data is not None and "Content-Type" not in headers:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            status = resp.getcode()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise HTTPError(e.code, body, url) from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"无法连接 {url}: {e.reason}") from e
    parsed = _json.loads(body) if body.strip() else {}
    return status, parsed


# 可被测试替换的全局传输实现。
TRANSPORT: Transport = _urllib_transport


def post_json(
    url: str, headers: dict, body: dict, timeout: float = 120.0
) -> dict:
    status, parsed = TRANSPORT("POST", url, headers, body, timeout)
    if status >= 400:
        raise HTTPError(status, _json.dumps(parsed), url)
    return parsed


def get_json(url: str, headers: dict, timeout: float = 30.0) -> dict:
    status, parsed = TRANSPORT("GET", url, headers, None, timeout)
    if status >= 400:
        raise HTTPError(status, _json.dumps(parsed), url)
    return parsed
