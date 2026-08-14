"""Versioned local NDJSON protocol for presentation clients."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping, TextIO

from modules.foundation.errors import MtbError, ValidationError
from modules.ui.service import get_state_value, load_snapshot, set_state_value

PROTOCOL = "mtb.bridge/1"
MAX_FRAME_BYTES = 1_048_576
_REQUEST_ID = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")


@dataclass(frozen=True)
class BridgeRequest:
    request_id: str
    operation: str
    payload: Mapping[str, Any]


class BridgeProtocolError(MtbError):
    """A recoverable client-frame validation error."""

    def __init__(self, code: str, message: str, request_id: str | None = None) -> None:
        super().__init__(code, message, request_id)


def _failure(request_id: str | None, code: str, message: str) -> dict[str, Any]:
    response: dict[str, Any] = {"protocol": PROTOCOL, "ok": False, "error": {"code": code, "message": message}}
    if request_id is not None:
        response["request_id"] = request_id
    return response


def parse_request(line: str) -> BridgeRequest:
    if len(line.encode("utf-8")) > MAX_FRAME_BYTES:
        raise BridgeProtocolError("frame-too-large", "Bridge frame exceeds the size limit.")
    try:
        raw = json.loads(line)
    except json.JSONDecodeError as error:
        raise BridgeProtocolError("invalid-json", "Bridge frame must be valid JSON.") from error
    if not isinstance(raw, dict):
        raise BridgeProtocolError("invalid-request", "Bridge request must be an object.")
    request_id = raw.get("request_id")
    if not isinstance(request_id, str) or not _REQUEST_ID.fullmatch(request_id):
        raise BridgeProtocolError("invalid-request-id", "Bridge request ID is invalid.")
    if raw.get("protocol") != PROTOCOL:
        raise BridgeProtocolError("unsupported-protocol", "Bridge protocol is unsupported.", request_id)
    operation = raw.get("operation")
    payload = raw.get("payload")
    if not isinstance(operation, str) or not isinstance(payload, dict):
        raise BridgeProtocolError("invalid-request", "Bridge operation and payload are invalid.", request_id)
    if set(raw) != {"protocol", "request_id", "operation", "payload"}:
        raise BridgeProtocolError("invalid-request", "Bridge request contains unsupported fields.", request_id)
    return BridgeRequest(request_id=request_id, operation=operation, payload=payload)


def _error_request_id(error: BridgeProtocolError) -> str | None:
    return error.detail if isinstance(error.detail, str) else None


def dispatch(request: BridgeRequest, state_dir, version: str) -> dict[str, Any]:
    if request.operation == "bridge.info":
        if request.payload:
            raise ValidationError("invalid-payload", "bridge.info does not accept payload values.")
        data = {"version": version, "operations": ["bridge.info", "view.snapshot", "view.refresh", "state.get", "state.set"]}
    elif request.operation in {"view.snapshot", "view.refresh"}:
        if request.payload:
            raise ValidationError("invalid-payload", "View operations do not accept payload values.")
        data = load_snapshot(state_dir, version).to_data()
    elif request.operation == "state.get":
        if set(request.payload) != {"key"}:
            raise ValidationError("invalid-payload", "state.get requires only key.")
        key = request.payload["key"]
        data = {"key": key, "value": get_state_value(state_dir, key)}
    elif request.operation == "state.set":
        if set(request.payload) != {"key", "value"}:
            raise ValidationError("invalid-payload", "state.set requires key and value.")
        key = request.payload["key"]
        data = {"key": key, "value": set_state_value(state_dir, key, request.payload["value"])}
    else:
        raise ValidationError("unknown-operation", "Bridge operation is not supported.")
    return {"protocol": PROTOCOL, "request_id": request.request_id, "ok": True, "data": data}


def serve(stdin: TextIO, stdout: TextIO, state_dir, version: str) -> None:
    for raw_line in stdin:
        request: BridgeRequest | None = None
        line = raw_line.rstrip("\r\n")
        if not line:
            response = _failure(None, "invalid-request", "Bridge frame must not be empty.")
        else:
            try:
                request = parse_request(line)
                response = dispatch(request, state_dir, version)
            except BridgeProtocolError as error:
                response = _failure(_error_request_id(error), error.code, error.message)
            except MtbError as error:
                response = _failure(request.request_id if request is not None else None, error.code, error.message)
        stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
        stdout.flush()
