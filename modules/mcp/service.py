"""Validated MCP definitions, managed receipts, and bridge-owned subprocesses."""

from __future__ import annotations

import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from modules.foundation.errors import ValidationError
from modules.foundation.storage import read_json, write_json_atomic

_SCHEMA_VERSION = 1
_ID = re.compile(r"[a-z][a-z0-9-]{0,62}\Z")
_ENV = re.compile(r"[A-Z_][A-Z0-9_]{0,127}\Z")


def _now() -> int:
    return int(time.time())


def _state_path(state_dir: Path) -> Path:
    return state_dir / "mcp.json"


def _validate_id(value: object, field: str = "MCP ID") -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValidationError("invalid-mcp-id", f"{field} must be a lower-case slug.")
    return value


def _validate_url(value: object) -> str:
    if not isinstance(value, str) or len(value) > 512:
        raise ValidationError("invalid-mcp-url", "MCP URL is invalid.")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValidationError("invalid-mcp-url", "Remote MCP URL must be an absolute HTTPS URL without credentials, query, or fragment.")
    return value.rstrip("/")


def _validate_args(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or (field == "MCP command" and not value) or len(value) > 32 or any(not isinstance(item, str) or not item or len(item) > 512 or "\x00" in item for item in value):
        raise ValidationError("invalid-mcp-command", f"{field} must be a string array; MCP commands cannot be empty.")
    return list(value)


def _validate_env_names(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > 32 or any(not isinstance(item, str) or not _ENV.fullmatch(item) for item in value):
        raise ValidationError("invalid-mcp-environment", "MCP environment values must be environment variable names.")
    return sorted(set(value))


@dataclass(frozen=True)
class McpDefinition:
    id: str
    name: str
    transport: str
    url: str | None
    command: tuple[str, ...]
    cwd: str | None
    environment: tuple[str, ...]
    risk_level: str
    enabled: bool
    updated_at: int

    def data(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "transport": self.transport, "url": self.url, "command": list(self.command), "cwd": self.cwd, "environment": list(self.environment), "risk_level": self.risk_level, "enabled": self.enabled, "updated_at": self.updated_at}

    def summary(self, managed: bool = True) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "transport": self.transport, "risk_level": self.risk_level, "enabled": self.enabled, "managed": managed, "environment_names": list(self.environment), "runtime_allowed": self.transport == "stdio" and managed}


def _definition(value: object) -> McpDefinition:
    if not isinstance(value, dict) or set(value) != {"id", "name", "transport", "url", "command", "cwd", "environment", "risk_level", "enabled", "updated_at"}:
        raise ValidationError("invalid-mcp-state", "Stored MCP definition is invalid.")
    identifier = _validate_id(value["id"])
    if not isinstance(value["name"], str) or not value["name"].strip() or len(value["name"].strip()) > 120:
        raise ValidationError("invalid-mcp-name", "MCP name is invalid.")
    if value["transport"] not in {"stdio", "https"}:
        raise ValidationError("invalid-mcp-transport", "MCP transport is not supported.")
    transport = value["transport"]
    url = _validate_url(value["url"]) if transport == "https" else None
    command = tuple(_validate_args(value["command"], "MCP command") if transport == "stdio" else [])
    cwd = value["cwd"]
    if cwd is not None and (not isinstance(cwd, str) or not cwd):
        raise ValidationError("invalid-mcp-cwd", "MCP working directory is invalid.")
    if value["risk_level"] not in {"low", "medium", "high"} or not isinstance(value["enabled"], bool) or not isinstance(value["updated_at"], int):
        raise ValidationError("invalid-mcp-state", "Stored MCP definition is invalid.")
    return McpDefinition(identifier, value["name"].strip(), transport, url, command, cwd, tuple(_validate_env_names(value["environment"])), value["risk_level"], value["enabled"], value["updated_at"])


class McpService:
    def __init__(self, state_dir: Path, environ: Mapping[str, str] | None = None) -> None:
        self.state_dir = state_dir
        self.environ = os.environ if environ is None else environ

    def _load(self) -> list[McpDefinition]:
        raw = read_json(_state_path(self.state_dir), {"schema_version": _SCHEMA_VERSION, "definitions": []})
        if not isinstance(raw, dict) or set(raw) != {"schema_version", "definitions"} or raw["schema_version"] != _SCHEMA_VERSION or not isinstance(raw["definitions"], list):
            raise ValidationError("invalid-mcp-state", "Stored MCP state is invalid.")
        definitions = [_definition(item) for item in raw["definitions"]]
        if len({item.id for item in definitions}) != len(definitions):
            raise ValidationError("invalid-mcp-state", "Stored MCP state contains duplicate IDs.")
        return definitions

    def _save(self, definitions: list[McpDefinition]) -> None:
        write_json_atomic(_state_path(self.state_dir), {"schema_version": _SCHEMA_VERSION, "definitions": [item.data() for item in sorted(definitions, key=lambda item: item.name.casefold())]})

    def list(self) -> dict[str, Any]:
        return {"servers": [item.summary() for item in self._load()]}

    def register(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if set(payload) != {"id", "name", "transport", "url", "command", "cwd", "environment", "risk_level"}:
            raise ValidationError("invalid-payload", "MCP definition fields are invalid.")
        raw = dict(payload)
        raw.update({"enabled": False, "updated_at": _now()})
        definition = _definition(raw)
        definitions = self._load()
        if any(item.id == definition.id for item in definitions):
            raise ValidationError("mcp-exists", "An MCP definition with this ID already exists.")
        if definition.transport == "stdio":
            cwd = Path(definition.cwd or self.state_dir).expanduser()
            if not cwd.exists() or not cwd.is_dir() or cwd.is_symlink():
                raise ValidationError("unsafe-mcp-cwd", "MCP working directory must be an existing regular directory.")
        definitions.append(definition)
        self._save(definitions)
        return definition.summary()

    def set_enabled(self, mcp_id: object, enabled: object) -> dict[str, Any]:
        identifier = _validate_id(mcp_id)
        if not isinstance(enabled, bool):
            raise ValidationError("invalid-mcp-enabled", "MCP enabled value is invalid.")
        definitions = self._load()
        for index, item in enumerate(definitions):
            if item.id == identifier:
                replacement = McpDefinition(item.id, item.name, item.transport, item.url, item.command, item.cwd, item.environment, item.risk_level, enabled, _now())
                definitions[index] = replacement
                self._save(definitions)
                return replacement.summary()
        raise ValidationError("mcp-missing", "MCP definition was not found.")

    def remove(self, mcp_id: object) -> None:
        identifier = _validate_id(mcp_id)
        definitions = self._load()
        retained = [item for item in definitions if item.id != identifier]
        if len(retained) == len(definitions):
            raise ValidationError("mcp-missing", "MCP definition was not found.")
        self._save(retained)

    def get(self, mcp_id: object) -> McpDefinition:
        identifier = _validate_id(mcp_id)
        for item in self._load():
            if item.id == identifier:
                return item
        raise ValidationError("mcp-missing", "MCP definition was not found.")


class McpRuntimeService:
    """Bridge-owned stdio MCP process runner; never executes shell strings."""

    def __init__(self, service: McpService) -> None:
        self.service = service
        self._processes: dict[str, subprocess.Popen[bytes]] = {}
        self._started: dict[str, int] = {}

    def status(self) -> dict[str, Any]:
        entries = []
        for item in self.service._load():
            process = self._processes.get(item.id)
            return_code = process.poll() if process is not None else None
            state = "stopped" if process is None else "healthy" if return_code is None else "exited"
            entries.append({"id": item.id, "state": state, "started_at": self._started.get(item.id), "exit_code": return_code, "transport": item.transport})
        return {"servers": entries}

    def start(self, mcp_id: object) -> dict[str, Any]:
        item = self.service.get(mcp_id)
        if not item.enabled:
            raise ValidationError("mcp-disabled", "Enable the MCP definition before starting it.")
        if item.transport != "stdio":
            raise ValidationError("remote-mcp-runtime", "Remote MCP services are configured but not launched locally.")
        process = self._processes.get(item.id)
        if process is not None and process.poll() is None:
            return {"id": item.id, "state": "healthy", "started_at": self._started[item.id], "exit_code": None}
        cwd = Path(item.cwd or self.service.state_dir).expanduser().resolve()
        if not cwd.is_dir() or cwd.is_symlink():
            raise ValidationError("unsafe-mcp-cwd", "MCP working directory is not safe to execute.")
        environment = {"PATH": self.service.environ.get("PATH", ""), "SYSTEMROOT": self.service.environ.get("SYSTEMROOT", "")}
        for name in item.environment:
            if name in self.service.environ:
                environment[name] = self.service.environ[name]
        try:
            process = subprocess.Popen(list(item.command), cwd=cwd, env=environment, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=False)
        except OSError as error:
            raise ValidationError("mcp-start-failed", "MCP process could not be started.") from error
        self._processes[item.id] = process
        self._started[item.id] = _now()
        return {"id": item.id, "state": "healthy" if process.poll() is None else "exited", "started_at": self._started[item.id], "exit_code": process.poll()}

    def stop(self, mcp_id: object) -> dict[str, Any]:
        identifier = _validate_id(mcp_id)
        process = self._processes.pop(identifier, None)
        self._started.pop(identifier, None)
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        return {"id": identifier, "state": "stopped", "started_at": None, "exit_code": process.poll() if process is not None else None}

    def close(self) -> None:
        for identifier in list(self._processes):
            self.stop(identifier)
