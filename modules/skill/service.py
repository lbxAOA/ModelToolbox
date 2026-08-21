"""Managed Skill metadata and conservative local inventory."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from modules.foundation.errors import ValidationError
from modules.foundation.paths import require_within
from modules.foundation.storage import read_json, write_json_atomic

_SCHEMA_VERSION = 1
_ID = re.compile(r"[a-z][a-z0-9-]{0,62}\Z")


def _path(state_dir: Path) -> Path:
    return state_dir / "skills.json"


def _validate_id(value: object) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValidationError("invalid-skill-id", "Skill ID must be a lower-case slug.")
    return value


class SkillService:
    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.root = state_dir / "managed-skills"

    def _load(self) -> list[dict[str, Any]]:
        raw = read_json(_path(self.state_dir), {"schema_version": _SCHEMA_VERSION, "skills": []})
        if not isinstance(raw, dict) or set(raw) != {"schema_version", "skills"} or raw["schema_version"] != _SCHEMA_VERSION or not isinstance(raw["skills"], list):
            raise ValidationError("invalid-skills", "Stored Skill state is invalid.")
        result: list[dict[str, Any]] = []
        for item in raw["skills"]:
            if not isinstance(item, dict) or set(item) != {"id", "name", "version", "enabled", "source", "risk_level"}:
                raise ValidationError("invalid-skills", "Stored Skill state is invalid.")
            if not isinstance(item["name"], str) or not item["name"].strip() or not isinstance(item["version"], str) or not item["version"] or not isinstance(item["enabled"], bool) or not isinstance(item["source"], str) or item["risk_level"] not in {"low", "medium", "high"}:
                raise ValidationError("invalid-skills", "Stored Skill state is invalid.")
            result.append({**item, "id": _validate_id(item["id"])})
        if len({item["id"] for item in result}) != len(result):
            raise ValidationError("invalid-skills", "Stored Skill state contains duplicate IDs.")
        return result

    def _save(self, skills: list[dict[str, Any]]) -> None:
        write_json_atomic(_path(self.state_dir), {"schema_version": _SCHEMA_VERSION, "skills": sorted(skills, key=lambda item: item["name"].casefold())})

    def list(self) -> dict[str, Any]:
        return {"skills": self._load()}

    def set_enabled(self, skill_id: object, enabled: object) -> dict[str, Any]:
        identifier = _validate_id(skill_id)
        if not isinstance(enabled, bool):
            raise ValidationError("invalid-skill-enabled", "Skill enabled value is invalid.")
        skills = self._load()
        for item in skills:
            if item["id"] == identifier:
                item["enabled"] = enabled
                self._save(skills)
                return item
        raise ValidationError("skill-missing", "Skill was not found.")

    def remove(self, skill_id: object) -> None:
        identifier = _validate_id(skill_id)
        skills = self._load()
        retained = [item for item in skills if item["id"] != identifier]
        if len(retained) == len(skills):
            raise ValidationError("skill-missing", "Skill was not found.")
        folder = require_within(self.root, self.root / identifier)
        if folder.exists() and not folder.is_symlink():
            import shutil
            shutil.rmtree(folder)
        self._save(retained)
