"""Atomic non-secret router route-policy state."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from modules.foundation.errors import ValidationError
from modules.foundation.storage import read_json, write_json_atomic
from modules.profiles.service import ProfileService

_PROTOCOLS = {"anthropic", "openai"}


@dataclass(frozen=True)
class RoutePolicy:
    profile_id: str
    inbound_protocol: str
    upstream_protocol: str
    upstream_url: str

    def to_data(self) -> dict[str, str]:
        return {
            "profile_id": self.profile_id,
            "inbound_protocol": self.inbound_protocol,
            "upstream_protocol": self.upstream_protocol,
            "upstream_url": self.upstream_url,
        }


def _path(state_dir: Path) -> Path:
    return state_dir / "router.json"


def _validate_url(value: object) -> str:
    if not isinstance(value, str):
        raise ValidationError("invalid-router-url", "Router upstream URL is invalid.")
    candidate = value.rstrip("/")
    parsed = urlparse(candidate)
    loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme not in {"https", "http"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or (parsed.scheme == "http" and not loopback):
        raise ValidationError("invalid-router-url", "Router upstream must be HTTPS or local loopback HTTP.")
    return candidate


def _validate_protocol(value: object) -> str:
    if value not in _PROTOCOLS:
        raise ValidationError("unsupported-router-protocol", "Router protocol is not supported.")
    return str(value)


def _validate_revision(value: object) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValidationError("invalid-router-revision", "Router revision is invalid.")
    return value


def _policy_from_data(value: object) -> RoutePolicy | None:
    if value is None:
        return None
    if not isinstance(value, Mapping) or set(value) != {"profile_id", "inbound_protocol", "upstream_protocol", "upstream_url"}:
        raise ValidationError("invalid-router-state", "Router state is invalid.")
    profile_id = value["profile_id"]
    if not isinstance(profile_id, str) or not profile_id:
        raise ValidationError("invalid-router-state", "Router state is invalid.")
    return RoutePolicy(
        profile_id=profile_id,
        inbound_protocol=_validate_protocol(value["inbound_protocol"]),
        upstream_protocol=_validate_protocol(value["upstream_protocol"]),
        upstream_url=_validate_url(value["upstream_url"]),
    )


class RouterPolicyService:
    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self._lock = threading.RLock()

    def _load(self) -> tuple[int, RoutePolicy | None, RoutePolicy | None]:
        raw = read_json(_path(self.state_dir), {"revision": 0, "active": None, "previous": None})
        if not isinstance(raw, dict) or set(raw) != {"revision", "active", "previous"}:
            raise ValidationError("invalid-router-state", "Router state is invalid.")
        return _validate_revision(raw["revision"]), _policy_from_data(raw["active"]), _policy_from_data(raw["previous"])

    def _save(self, revision: int, active: RoutePolicy | None, previous: RoutePolicy | None) -> None:
        write_json_atomic(_path(self.state_dir), {
            "revision": revision,
            "active": None if active is None else active.to_data(),
            "previous": None if previous is None else previous.to_data(),
        })

    @staticmethod
    def _status(revision: int, active: RoutePolicy | None, previous: RoutePolicy | None) -> dict[str, Any]:
        return {
            "revision": revision,
            "active": None if active is None else active.to_data(),
            "previous": None if previous is None else previous.to_data(),
            "state": "active" if active else "direct",
        }

    def status(self) -> dict[str, Any]:
        with self._lock:
            return self._status(*self._load())

    def plan_activate(self, profile_id: object, inbound_protocol: object, upstream_protocol: object) -> dict[str, Any]:
        inbound = _validate_protocol(inbound_protocol)
        upstream = _validate_protocol(upstream_protocol)
        profile = ProfileService(self.state_dir).get(profile_id)
        proposed = RoutePolicy(profile_id=profile["id"], inbound_protocol=inbound, upstream_protocol=upstream, upstream_url=_validate_url(profile["base_url"]))
        with self._lock:
            revision, active, previous = self._load()
        changes = [] if active == proposed else [{"field": key, "from": None if active is None else active.to_data()[key], "to": proposed.to_data()[key]} for key in proposed.to_data() if active is None or active.to_data()[key] != proposed.to_data()[key]]
        return {
            "revision": revision,
            "next_revision": revision + 1,
            "active": None if active is None else active.to_data(),
            "previous": None if previous is None else previous.to_data(),
            "proposed": proposed.to_data(),
            "changes": changes,
            "ready": bool(changes),
            "message": "The local router supports bounded non-streaming text requests only.",
        }

    def activate(self, profile_id: object, inbound_protocol: object, upstream_protocol: object, expected_revision: object) -> dict[str, Any]:
        inbound = _validate_protocol(inbound_protocol)
        upstream = _validate_protocol(upstream_protocol)
        expected = _validate_revision(expected_revision)
        profile = ProfileService(self.state_dir).get(profile_id)
        proposed = RoutePolicy(profile_id=profile["id"], inbound_protocol=inbound, upstream_protocol=upstream, upstream_url=_validate_url(profile["base_url"]))
        with self._lock:
            revision, active, _ = self._load()
            if revision != expected:
                raise ValidationError("router-policy-changed", "Router policy changed; preview again before applying.")
            self._save(revision + 1, proposed, active)
            return self._status(revision + 1, proposed, active)

    def rollback(self, expected_revision: object) -> dict[str, Any]:
        expected = _validate_revision(expected_revision)
        with self._lock:
            revision, active, previous = self._load()
            if revision != expected:
                raise ValidationError("router-policy-changed", "Router policy changed; refresh before rolling back.")
            if previous is None:
                raise ValidationError("router-no-rollback", "Router has no previous policy.")
            self._save(revision + 1, previous, active)
            return self._status(revision + 1, previous, active)

    def direct(self, expected_revision: object) -> dict[str, Any]:
        expected = _validate_revision(expected_revision)
        with self._lock:
            revision, active, _ = self._load()
            if revision != expected:
                raise ValidationError("router-policy-changed", "Router policy changed; refresh before entering direct mode.")
            self._save(revision + 1, None, active)
            return self._status(revision + 1, None, active)
