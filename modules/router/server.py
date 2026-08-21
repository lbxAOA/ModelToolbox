"""Loopback-only HTTP protocol router for the verified text subset."""

from __future__ import annotations

import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from modules.foundation.errors import MtbError, ValidationError
from modules.router.activity import ActivityLog
from modules.router.policy import RouterPolicyService
from modules.router.protocols import anthropic, openai
from modules.router.upstream import forward

_MAX_REQUEST = 1_000_000


def _json(handler: BaseHTTPRequestHandler, status: int, value: object) -> None:
    body = json.dumps(value, separators=(",", ":")).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _error(handler: BaseHTTPRequestHandler, status: int, code: str, message: str) -> None:
    _json(handler, status, {"error": {"code": code, "message": message}})


def _make_handler(policy: RouterPolicyService, activity: ActivityLog):
    class Handler(BaseHTTPRequestHandler):
        server_version = "ModelToolboxRouter/0.1"

        def log_message(self, *_: object) -> None:
            return

        def do_POST(self) -> None:
            started = time.monotonic()
            inbound = "anthropic" if self.path == "/v1/messages" else "openai" if self.path == "/v1/chat/completions" else None
            if inbound is None:
                _error(self, 404, "router-route-missing", "Router route is not supported.")
                return
            try:
                length = int(self.headers.get("Content-Length", "-1"))
                if not 0 <= length <= _MAX_REQUEST:
                    raise ValidationError("router-request-too-large", "Router request exceeded the limit.")
                raw = self.rfile.read(length)
                request = json.loads(raw.decode("utf-8"))
                snapshot = policy.status()
                active = snapshot["active"]
                if active is None or active["inbound_protocol"] != inbound:
                    raise ValidationError("router-no-policy", "Router has no active compatible route policy.")
                exchange = anthropic.parse_request(request) if inbound == "anthropic" else openai.parse_request(request)
                upstream = active["upstream_protocol"]
                payload = openai.render_request(exchange) if upstream == "openai" else {"model": exchange.model, "max_tokens": exchange.max_tokens, "messages": [{"role": item.role, "content": item.text} for item in exchange.messages if item.role != "system"], "system": "\n".join(item.text for item in exchange.messages if item.role == "system") or None}
                if payload.get("system") is None: payload.pop("system", None)
                authorization = self.headers.get("Authorization")
                status, result = forward(active["upstream_url"], "/v1/chat/completions" if upstream == "openai" else "/v1/messages", payload, authorization)
                rendered = openai.render_response(result) if upstream == "openai" else anthropic.render_response(result)
                output: dict[str, Any]
                if inbound == "anthropic":
                    output = {"type": "message", "role": "assistant", "model": rendered["model"] or exchange.model, "content": [{"type": "text", "text": rendered["text"]}], "stop_reason": "end_turn"}
                else:
                    output = {"object": "chat.completion", "model": rendered["model"] or exchange.model, "choices": [{"index": 0, "message": {"role": "assistant", "content": rendered["text"]}, "finish_reason": "stop"}]}
                activity.append(snapshot["revision"], inbound, upstream, "success", status, int((time.monotonic() - started) * 1000))
                _json(self, status, output)
            except MtbError as error:
                activity.append(policy.status()["revision"], inbound or "unknown", "unknown", error.code, None, int((time.monotonic() - started) * 1000))
                _error(self, 400, error.code, error.message)
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
                _error(self, 400, "invalid-router-json", "Router request was invalid JSON.")
    return Handler


def serve(state_dir, host: str = "127.0.0.1", port: int = 15721, *, policy: RouterPolicyService | None = None, activity: ActivityLog | None = None) -> None:
    if host != "127.0.0.1":
        raise ValidationError("router-bind-rejected", "Router may bind only to loopback.")
    server = ThreadingHTTPServer((host, port), _make_handler(policy or RouterPolicyService(state_dir), activity or ActivityLog()))
    try:
        server.serve_forever(poll_interval=0.2)
    finally:
        server.server_close()
