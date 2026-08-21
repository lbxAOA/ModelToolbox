"""Versioned local NDJSON protocol for presentation clients."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping, TextIO

from modules.foundation.errors import MtbError, ValidationError
from modules.integrations.service import IntegrationService
from modules.marketplace.service import MarketplaceService
from modules.mcp.service import McpRuntimeService, McpService
from modules.profiles.service import ProfileService
from modules.router.policy import RouterPolicyService
from modules.router.runtime import RouterRuntimeService
from modules.skill.service import SkillService
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


def dispatch(request: BridgeRequest, state_dir, version: str, *, profiles: ProfileService | None = None, router: RouterPolicyService | None = None, runtime: RouterRuntimeService | None = None, integrations: IntegrationService | None = None, mcp: McpService | None = None, mcp_runtime: McpRuntimeService | None = None, skills: SkillService | None = None, marketplace: MarketplaceService | None = None) -> dict[str, Any]:
    profiles = profiles or ProfileService(state_dir)
    router = router or RouterPolicyService(state_dir)
    runtime = runtime or RouterRuntimeService(state_dir, router)
    integrations = integrations or IntegrationService()
    mcp = mcp or McpService(state_dir)
    mcp_runtime = mcp_runtime or McpRuntimeService(mcp)
    skills = skills or SkillService(state_dir)
    marketplace = marketplace or MarketplaceService(state_dir)
    if request.operation == "bridge.info":
        if request.payload:
            raise ValidationError("invalid-payload", "bridge.info does not accept payload values.")
        data = {"version": version, "operations": ["bridge.info", "view.snapshot", "view.refresh", "state.get", "state.set", "profiles.adapters", "profiles.list", "profiles.get", "profiles.create", "profiles.update", "profiles.select", "profiles.delete", "profiles.inspect", "profiles.plan-apply", "profiles.apply", "router.status", "router.plan-activate", "router.activate", "router.rollback", "router.direct", "router.listener-status", "router.listener-start", "router.listener-stop", "router.activity", "integrations.list", "integrations.inspect", "mcp.list", "mcp.register", "mcp.enable", "mcp.remove", "mcp.status", "mcp.start", "mcp.stop", "skills.list", "skills.enable", "skills.remove", "marketplace.status", "marketplace.catalog", "marketplace.recommendations"]}
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
    elif request.operation == "router.status":
        if request.payload:
            raise ValidationError("invalid-payload", "router.status does not accept payload values.")
        data = router.status()
    elif request.operation == "router.plan-activate":
        if set(request.payload) != {"profile_id", "inbound_protocol", "upstream_protocol"}:
            raise ValidationError("invalid-payload", "router.plan-activate requires profile_id and protocols.")
        data = router.plan_activate(request.payload["profile_id"], request.payload["inbound_protocol"], request.payload["upstream_protocol"])
    elif request.operation == "router.activate":
        if set(request.payload) != {"profile_id", "inbound_protocol", "upstream_protocol", "expected_revision"}:
            raise ValidationError("invalid-payload", "router.activate requires profile_id, protocols, and expected revision.")
        data = router.activate(request.payload["profile_id"], request.payload["inbound_protocol"], request.payload["upstream_protocol"], request.payload["expected_revision"])
    elif request.operation == "router.rollback":
        if set(request.payload) != {"expected_revision"}:
            raise ValidationError("invalid-payload", "router.rollback requires expected revision.")
        data = router.rollback(request.payload["expected_revision"])
    elif request.operation == "router.direct":
        if set(request.payload) != {"expected_revision"}:
            raise ValidationError("invalid-payload", "router.direct requires expected revision.")
        data = router.direct(request.payload["expected_revision"])
    elif request.operation == "router.listener-status":
        if request.payload:
            raise ValidationError("invalid-payload", "router.listener-status does not accept payload values.")
        data = runtime.status()
    elif request.operation == "router.listener-start":
        if set(request.payload) != {"host", "port"}:
            raise ValidationError("invalid-payload", "router.listener-start requires host and port.")
        data = runtime.start(request.payload["host"], request.payload["port"])
    elif request.operation == "router.listener-stop":
        if request.payload:
            raise ValidationError("invalid-payload", "router.listener-stop does not accept payload values.")
        data = runtime.stop()
    elif request.operation == "router.activity":
        if request.payload:
            raise ValidationError("invalid-payload", "router.activity does not accept payload values.")
        data = runtime.activity_list()
    elif request.operation == "profiles.adapters":
        if request.payload:
            raise ValidationError("invalid-payload", "profiles.adapters does not accept payload values.")
        data = profiles.list_adapters()
    elif request.operation == "profiles.list":
        if request.payload:
            raise ValidationError("invalid-payload", "profiles.list does not accept payload values.")
        data = profiles.list()
    elif request.operation == "profiles.get":
        if set(request.payload) != {"profile_id"}:
            raise ValidationError("invalid-payload", "profiles.get requires only profile_id.")
        data = profiles.get(request.payload["profile_id"])
    elif request.operation == "profiles.create":
        data = profiles.create(request.payload)
    elif request.operation == "profiles.update":
        if set(request.payload) != {"profile_id", "profile"} or not isinstance(request.payload["profile"], dict):
            raise ValidationError("invalid-payload", "profiles.update requires profile_id and profile.")
        data = profiles.update(request.payload["profile_id"], request.payload["profile"])
    elif request.operation == "profiles.select":
        if set(request.payload) != {"profile_id"}:
            raise ValidationError("invalid-payload", "profiles.select requires only profile_id.")
        data = profiles.select(request.payload["profile_id"])
    elif request.operation == "profiles.delete":
        if set(request.payload) != {"profile_id"}:
            raise ValidationError("invalid-payload", "profiles.delete requires only profile_id.")
        profiles.delete(request.payload["profile_id"])
        data = {"deleted": True}
    elif request.operation == "profiles.inspect":
        if set(request.payload) != {"profile_id"}:
            raise ValidationError("invalid-payload", "profiles.inspect requires only profile_id.")
        data = profiles.inspect(request.payload["profile_id"])
    elif request.operation == "profiles.plan-apply":
        if set(request.payload) != {"profile_id"}:
            raise ValidationError("invalid-payload", "profiles.plan-apply requires only profile_id.")
        data = profiles.plan_apply(request.payload["profile_id"])
    elif request.operation == "profiles.apply":
        if set(request.payload) != {"profile_id", "revision"}:
            raise ValidationError("invalid-payload", "profiles.apply requires profile_id and revision.")
        data = profiles.apply(request.payload["profile_id"], request.payload["revision"])
    elif request.operation == "integrations.list":
        if request.payload:
            raise ValidationError("invalid-payload", "integrations.list does not accept payload values.")
        data = integrations.list()
    elif request.operation == "integrations.inspect":
        if set(request.payload) != {"adapter_id"}:
            raise ValidationError("invalid-payload", "integrations.inspect requires only adapter_id.")
        data = integrations.inspect(request.payload["adapter_id"])
    elif request.operation == "mcp.list":
        if request.payload:
            raise ValidationError("invalid-payload", "mcp.list does not accept payload values.")
        data = mcp.list()
    elif request.operation == "mcp.register":
        data = mcp.register(request.payload)
    elif request.operation == "mcp.enable":
        if set(request.payload) != {"mcp_id", "enabled"}:
            raise ValidationError("invalid-payload", "mcp.enable requires mcp_id and enabled.")
        data = mcp.set_enabled(request.payload["mcp_id"], request.payload["enabled"])
    elif request.operation == "mcp.remove":
        if set(request.payload) != {"mcp_id"}:
            raise ValidationError("invalid-payload", "mcp.remove requires only mcp_id.")
        mcp.remove(request.payload["mcp_id"])
        data = {"removed": True}
    elif request.operation == "mcp.status":
        if request.payload:
            raise ValidationError("invalid-payload", "mcp.status does not accept payload values.")
        data = mcp_runtime.status()
    elif request.operation == "mcp.start":
        if set(request.payload) != {"mcp_id"}:
            raise ValidationError("invalid-payload", "mcp.start requires only mcp_id.")
        data = mcp_runtime.start(request.payload["mcp_id"])
    elif request.operation == "mcp.stop":
        if set(request.payload) != {"mcp_id"}:
            raise ValidationError("invalid-payload", "mcp.stop requires only mcp_id.")
        data = mcp_runtime.stop(request.payload["mcp_id"])
    elif request.operation == "skills.list":
        if request.payload:
            raise ValidationError("invalid-payload", "skills.list does not accept payload values.")
        data = skills.list()
    elif request.operation == "skills.enable":
        if set(request.payload) != {"skill_id", "enabled"}:
            raise ValidationError("invalid-payload", "skills.enable requires skill_id and enabled.")
        data = skills.set_enabled(request.payload["skill_id"], request.payload["enabled"])
    elif request.operation == "skills.remove":
        if set(request.payload) != {"skill_id"}:
            raise ValidationError("invalid-payload", "skills.remove requires only skill_id.")
        skills.remove(request.payload["skill_id"])
        data = {"removed": True}
    elif request.operation == "marketplace.status":
        if request.payload:
            raise ValidationError("invalid-payload", "marketplace.status does not accept payload values.")
        data = marketplace.status()
    elif request.operation == "marketplace.catalog":
        if set(request.payload) != {"query"}:
            raise ValidationError("invalid-payload", "marketplace.catalog requires only query.")
        data = marketplace.catalog(request.payload["query"])
    elif request.operation == "marketplace.recommendations":
        if request.payload:
            raise ValidationError("invalid-payload", "marketplace.recommendations does not accept payload values.")
        data = marketplace.recommendations()
    else:
        raise ValidationError("unknown-operation", "Bridge operation is not supported.")
    return {"protocol": PROTOCOL, "request_id": request.request_id, "ok": True, "data": data}


def serve(stdin: TextIO, stdout: TextIO, state_dir, version: str) -> None:
    profiles = ProfileService(state_dir)
    router = RouterPolicyService(state_dir)
    runtime = RouterRuntimeService(state_dir, router)
    integrations = IntegrationService()
    mcp = McpService(state_dir)
    mcp_runtime = McpRuntimeService(mcp)
    skills = SkillService(state_dir)
    marketplace = MarketplaceService(state_dir)
    try:
        for raw_line in stdin:
            request: BridgeRequest | None = None
            line = raw_line.rstrip("\r\n")
            if not line:
                response = _failure(None, "invalid-request", "Bridge frame must not be empty.")
            else:
                try:
                    request = parse_request(line)
                    response = dispatch(request, state_dir, version, profiles=profiles, router=router, runtime=runtime, integrations=integrations, mcp=mcp, mcp_runtime=mcp_runtime, skills=skills, marketplace=marketplace)
                except BridgeProtocolError as error:
                    response = _failure(_error_request_id(error), error.code, error.message)
                except MtbError as error:
                    response = _failure(request.request_id if request is not None else None, error.code, error.message)
            stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
            stdout.flush()
    finally:
        mcp_runtime.close()
        if runtime.status()["running"]:
            runtime.stop()
