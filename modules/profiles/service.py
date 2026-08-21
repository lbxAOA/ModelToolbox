"""Non-secret profile records, validated storage, and guarded local adapters."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from modules.foundation.errors import ValidationError
from modules.foundation.storage import read_json, write_json_atomic

_SCHEMA_VERSION = 1
_PROFILE_ID = re.compile(r"[a-z][a-z0-9-]{0,62}\Z")
_ENV_NAME = re.compile(r"[A-Z_][A-Z0-9_]{0,127}\Z")
_NAME_LIMIT = 80
_URL_LIMIT = 512
_ADAPTERS = {
    "claude-code": {"name": "Claude Code", "contract_status": "verified", "write_enabled": True, "message": "Claude Code user settings are enabled for non-secret endpoint and model fields."},
    "codex-cli": {"name": "Codex CLI", "contract_status": "unverified", "write_enabled": False, "message": "Codex CLI configuration is not enabled until its local contract is verified."},
    "codex-desktop": {"name": "Codex Desktop", "contract_status": "unknown", "write_enabled": False, "message": "Codex Desktop configuration is unavailable until its local contract is verified."},
    "claude-desktop": {"name": "Claude Desktop", "contract_status": "unknown", "write_enabled": False, "message": "Claude Desktop configuration is unavailable until its local contract is verified."},
}
_SUPPORTED_ADAPTERS = set(_ADAPTERS)


@dataclass(frozen=True)
class Profile:
    id: str
    name: str
    adapter_id: str
    base_url: str
    model: str | None
    credential_source: str | None
    updated_at: int

    def summary(self, selected_id: str | None) -> dict[str, Any]:
        adapter = _ADAPTERS[self.adapter_id]
        return {
            "id": self.id,
            "name": self.name,
            "adapter_id": self.adapter_id,
            "adapter_name": adapter["name"],
            "adapter_available": adapter["write_enabled"],
            "adapter_message": adapter["message"],
            "base_url": self.base_url,
            "model": self.model,
            "credential_status": "not-managed",
            "selected": self.id == selected_id,
        }


def profiles_path(state_dir: Path) -> Path:
    return state_dir / "profiles.json"


def _now() -> int:
    return int(time.time())


def _validate_id(value: object) -> str:
    if not isinstance(value, str) or not _PROFILE_ID.fullmatch(value):
        raise ValidationError("invalid-profile-id", "Profile ID must be a lower-case slug.")
    return value


def _validate_name(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > _NAME_LIMIT:
        raise ValidationError("invalid-profile-name", "Profile name must be between 1 and 80 characters.")
    return value.strip()


def _validate_adapter(value: object) -> str:
    if value not in _SUPPORTED_ADAPTERS:
        raise ValidationError("invalid-profile-adapter", "Profile adapter is not supported.")
    return str(value)


def _validate_url(value: object) -> str:
    if not isinstance(value, str) or len(value) > _URL_LIMIT:
        raise ValidationError("invalid-base-url", "Base URL is invalid.")
    candidate = value.strip().rstrip("/")
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValidationError("invalid-base-url", "Base URL must be an absolute HTTP or HTTPS URL.")
    loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not loopback:
        raise ValidationError("insecure-base-url", "HTTP URLs are allowed only for local loopback services.")
    return candidate


def _validate_model(value: object) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str) or len(value) > 160 or any(character.isspace() for character in value):
        raise ValidationError("invalid-profile-model", "Model must be a short non-space identifier.")
    return value


def _validate_credential_source(value: object) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str) or not _ENV_NAME.fullmatch(value):
        raise ValidationError("invalid-credential-source", "Credential source must be an environment variable name.")
    return value


def _profile_from_data(value: object) -> Profile:
    if not isinstance(value, dict) or set(value) != {"id", "name", "adapter_id", "base_url", "model", "credential_source", "updated_at"}:
        raise ValidationError("invalid-profiles", "Stored profile data is invalid.")
    updated_at = value["updated_at"]
    if not isinstance(updated_at, int) or updated_at < 0:
        raise ValidationError("invalid-profiles", "Stored profile data is invalid.")
    return Profile(
        id=_validate_id(value["id"]),
        name=_validate_name(value["name"]),
        adapter_id=_validate_adapter(value["adapter_id"]),
        base_url=_validate_url(value["base_url"]),
        model=_validate_model(value["model"]),
        credential_source=_validate_credential_source(value["credential_source"]),
        updated_at=updated_at,
    )


def _profile_data(profile: Profile) -> dict[str, Any]:
    return {
        "id": profile.id,
        "name": profile.name,
        "adapter_id": profile.adapter_id,
        "base_url": profile.base_url,
        "model": profile.model,
        "credential_source": profile.credential_source,
        "updated_at": profile.updated_at,
    }


class ProfileService:
    """Owns non-secret profiles and only adapter-allowlisted file modifications."""

    def __init__(self, state_dir: Path, environ: Mapping[str, str] | None = None) -> None:
        self.state_dir = state_dir
        self.environ = os.environ if environ is None else environ

    def _load(self) -> tuple[str | None, list[Profile]]:
        raw = read_json(profiles_path(self.state_dir), {"schema_version": _SCHEMA_VERSION, "selected_profile_id": None, "profiles": []})
        if not isinstance(raw, dict) or set(raw) != {"schema_version", "selected_profile_id", "profiles"} or raw["schema_version"] != _SCHEMA_VERSION:
            raise ValidationError("invalid-profiles", "Stored profile data is invalid.")
        selected = raw["selected_profile_id"]
        if selected is not None:
            selected = _validate_id(selected)
        if not isinstance(raw["profiles"], list):
            raise ValidationError("invalid-profiles", "Stored profile data is invalid.")
        profiles = [_profile_from_data(item) for item in raw["profiles"]]
        if len({profile.id for profile in profiles}) != len(profiles) or len({profile.name.casefold() for profile in profiles}) != len(profiles):
            raise ValidationError("invalid-profiles", "Stored profile data contains duplicate names or IDs.")
        if selected is not None and selected not in {profile.id for profile in profiles}:
            raise ValidationError("invalid-profiles", "Selected profile does not exist.")
        return selected, profiles

    def _save(self, selected: str | None, profiles: list[Profile]) -> None:
        write_json_atomic(profiles_path(self.state_dir), {
            "schema_version": _SCHEMA_VERSION,
            "selected_profile_id": selected,
            "profiles": [_profile_data(profile) for profile in sorted(profiles, key=lambda item: item.name.casefold())],
        })

    def list_adapters(self) -> dict[str, Any]:
        return {"adapters": [
            {
                "id": adapter_id,
                "name": metadata["name"],
                "contract_status": metadata["contract_status"],
                "available": metadata["write_enabled"],
                "write_enabled": metadata["write_enabled"],
                "message": metadata["message"],
            }
            for adapter_id, metadata in _ADAPTERS.items()
        ]}

    def list(self) -> dict[str, Any]:
        selected, profiles = self._load()
        return {"selected_profile_id": selected, "profiles": [profile.summary(selected) for profile in sorted(profiles, key=lambda item: item.name.casefold())]}

    def get(self, profile_id: object) -> dict[str, Any]:
        selected, profiles = self._load()
        profile = self._find(profiles, _validate_id(profile_id))
        return profile.summary(selected)

    def create(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if set(payload) != {"id", "name", "adapter_id", "base_url", "model", "credential_source"}:
            raise ValidationError("invalid-payload", "Profile fields are invalid.")
        selected, profiles = self._load()
        profile = Profile(_validate_id(payload["id"]), _validate_name(payload["name"]), _validate_adapter(payload["adapter_id"]), _validate_url(payload["base_url"]), _validate_model(payload["model"]), _validate_credential_source(payload["credential_source"]), _now())
        if any(item.id == profile.id or item.name.casefold() == profile.name.casefold() for item in profiles):
            raise ValidationError("profile-exists", "A profile with this ID or name already exists.")
        profiles.append(profile)
        self._save(selected, profiles)
        return profile.summary(selected)

    def update(self, profile_id: object, payload: Mapping[str, Any]) -> dict[str, Any]:
        if set(payload) != {"name", "base_url", "model", "credential_source"}:
            raise ValidationError("invalid-payload", "Profile update fields are invalid.")
        selected, profiles = self._load()
        profile = self._find(profiles, _validate_id(profile_id))
        updated = replace(profile, name=_validate_name(payload["name"]), base_url=_validate_url(payload["base_url"]), model=_validate_model(payload["model"]), credential_source=_validate_credential_source(payload["credential_source"]), updated_at=_now())
        if any(item.id != updated.id and item.name.casefold() == updated.name.casefold() for item in profiles):
            raise ValidationError("profile-exists", "A profile with this name already exists.")
        profiles[profiles.index(profile)] = updated
        self._save(selected, profiles)
        return updated.summary(selected)

    def select(self, profile_id: object) -> dict[str, Any]:
        _, profiles = self._load()
        profile = self._find(profiles, _validate_id(profile_id))
        self._save(profile.id, profiles)
        return profile.summary(profile.id)

    def delete(self, profile_id: object) -> None:
        selected, profiles = self._load()
        profile = self._find(profiles, _validate_id(profile_id))
        profiles.remove(profile)
        self._save(None if selected == profile.id else selected, profiles)

    def inspect(self, profile_id: object) -> dict[str, Any]:
        profile = self._find(self._load()[1], _validate_id(profile_id))
        adapter = _ADAPTERS[profile.adapter_id]
        if not adapter["write_enabled"]:
            return {"profile_id": profile.id, "status": "unavailable", "target": adapter["name"], "revision": None, "values": {}, "message": adapter["message"]}
        path = self._adapter_path(profile.adapter_id)
        if not path.exists():
            return {"profile_id": profile.id, "status": "missing", "target": self._target_label(profile.adapter_id), "revision": None, "values": {}}
        if path.is_symlink() or not path.is_file():
            raise ValidationError("unsafe-target-config", "Target configuration is not a regular file.")
        raw = path.read_bytes()
        values = self._read_adapter(profile.adapter_id, raw)
        return {"profile_id": profile.id, "status": "ready", "target": self._target_label(profile.adapter_id), "revision": hashlib.sha256(raw).hexdigest(), "values": values}

    def plan_apply(self, profile_id: object) -> dict[str, Any]:
        profile = self._find(self._load()[1], _validate_id(profile_id))
        inspection = self.inspect(profile.id)
        if inspection["status"] == "unavailable":
            return {"profile_id": profile.id, "target": inspection["target"], "revision": None, "changes": [], "ready": False, "status": "unavailable", "message": inspection["message"]}
        if inspection["status"] != "ready":
            raise ValidationError("target-config-missing", "Target configuration was not found; create it in the target application first.")
        desired = self._managed_values(profile)
        changes = [{"field": key, "from": inspection["values"].get(key), "to": value} for key, value in desired.items() if inspection["values"].get(key) != value]
        return {"profile_id": profile.id, "target": inspection["target"], "revision": inspection["revision"], "changes": changes, "ready": bool(changes)}

    def apply(self, profile_id: object, revision: object) -> dict[str, Any]:
        if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{64}", revision):
            raise ValidationError("invalid-revision", "Apply requires a valid preview revision.")
        profile = self._find(self._load()[1], _validate_id(profile_id))
        adapter = _ADAPTERS[profile.adapter_id]
        if not adapter["write_enabled"]:
            raise ValidationError("adapter-unavailable", adapter["message"])
        inspection = self.inspect(profile.id)
        if inspection["status"] != "ready" or inspection["revision"] != revision:
            raise ValidationError("target-config-changed", "Target configuration changed; inspect and preview again.")
        path = self._adapter_path(profile.adapter_id)
        original = path.read_bytes()
        updated = self._write_adapter(profile.adapter_id, original, self._managed_values(profile))
        backup = path.with_suffix(path.suffix + ".modeltoolbox-backup")
        shutil.copyfile(path, backup)
        path.write_bytes(updated)
        verified = self.inspect(profile.id)
        verified_values = verified["values"]
        if any(verified_values.get(key) != value for key, value in self._managed_values(profile).items()):
            path.write_bytes(original)
            raise ValidationError("apply-verification-failed", "Target configuration could not be verified and was restored.")
        return {"profile_id": profile.id, "target": self._target_label(profile.adapter_id), "applied": True}

    @staticmethod
    def _find(profiles: list[Profile], profile_id: str) -> Profile:
        for profile in profiles:
            if profile.id == profile_id:
                return profile
        raise ValidationError("profile-missing", "Profile was not found.")

    def _adapter_path(self, adapter_id: str) -> Path:
        home = Path(self.environ.get("USERPROFILE") or self.environ.get("HOME") or Path.home())
        return home / (".claude/settings.json" if adapter_id == "claude-code" else ".codex/config.toml")

    @staticmethod
    def _target_label(adapter_id: str) -> str:
        return _ADAPTERS[adapter_id]["name"]

    @staticmethod
    def _managed_values(profile: Profile) -> dict[str, str | None]:
        return {"base_url": profile.base_url, "model": profile.model}

    @staticmethod
    def _read_adapter(adapter_id: str, raw: bytes) -> dict[str, str]:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValidationError("invalid-target-config", "Target configuration must be UTF-8 text.") from error
        if adapter_id == "claude-code":
            try:
                config = json.loads(text)
            except json.JSONDecodeError as error:
                raise ValidationError("invalid-target-config", "Claude Code settings must be valid JSON.") from error
            if not isinstance(config, dict) or ("env" in config and not isinstance(config["env"], dict)):
                raise ValidationError("invalid-target-config", "Claude Code settings structure is invalid.")
            env = config.get("env", {})
            values: dict[str, str] = {}
            if isinstance(env.get("ANTHROPIC_BASE_URL"), str): values["base_url"] = env["ANTHROPIC_BASE_URL"]
            if isinstance(env.get("ANTHROPIC_MODEL"), str): values["model"] = env["ANTHROPIC_MODEL"]
            return values
        values = {}
        for line in text.splitlines():
            key, separator, value = line.partition("=")
            if separator and key.strip() in {"base_url", "model"}:
                values[key.strip()] = value.strip().strip('"')
        return values

    @staticmethod
    def _write_adapter(adapter_id: str, raw: bytes, desired: Mapping[str, str | None]) -> bytes:
        if adapter_id == "claude-code":
            config = json.loads(raw.decode("utf-8"))
            env = config.setdefault("env", {})
            env["ANTHROPIC_BASE_URL"] = desired["base_url"]
            if desired["model"] is None:
                env.pop("ANTHROPIC_MODEL", None)
            else:
                env["ANTHROPIC_MODEL"] = desired["model"]
            return (json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        text = raw.decode("utf-8")
        lines = text.splitlines()
        updated: set[str] = set()
        result: list[str] = []
        for line in lines:
            key, separator, _ = line.partition("=")
            normalized = key.strip()
            if separator and normalized in desired:
                if desired[normalized] is not None:
                    result.append(f'{normalized} = "{desired[normalized]}"')
                updated.add(normalized)
            else:
                result.append(line)
        for key, value in desired.items():
            if key not in updated and value is not None:
                result.append(f'{key} = "{value}"')
        return ("\n".join(result) + "\n").encode("utf-8")
