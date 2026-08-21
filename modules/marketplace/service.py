"""Opt-in trusted marketplace cache and deterministic recommendations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.foundation.errors import ValidationError
from modules.foundation.storage import read_json, write_json_atomic

_SCHEMA_VERSION = 1


def _path(state_dir: Path) -> Path:
    return state_dir / "marketplace.json"


class MarketplaceService:
    """Catalog is local by default; remote refresh is intentionally not implicit."""

    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir

    def _load(self) -> dict[str, Any]:
        raw = read_json(_path(self.state_dir), {"schema_version": _SCHEMA_VERSION, "online_enabled": False, "catalog": []})
        if not isinstance(raw, dict) or set(raw) != {"schema_version", "online_enabled", "catalog"} or raw["schema_version"] != _SCHEMA_VERSION or not isinstance(raw["online_enabled"], bool) or not isinstance(raw["catalog"], list):
            raise ValidationError("invalid-marketplace", "Marketplace cache is invalid.")
        catalog: list[dict[str, Any]] = []
        for item in raw["catalog"]:
            if not isinstance(item, dict) or set(item) != {"id", "kind", "name", "version", "description", "source", "trust", "risk_level", "compatible_adapters", "tags", "installable"}:
                raise ValidationError("invalid-marketplace", "Marketplace catalog entry is invalid.")
            if not isinstance(item["id"], str) or not isinstance(item["kind"], str) or item["kind"] not in {"mcp", "skill"} or not isinstance(item["name"], str) or not isinstance(item["version"], str) or not isinstance(item["description"], str) or not isinstance(item["source"], str) or item["trust"] not in {"trusted", "community"} or item["risk_level"] not in {"low", "medium", "high"} or not isinstance(item["compatible_adapters"], list) or not all(isinstance(value, str) for value in item["compatible_adapters"]) or not isinstance(item["tags"], list) or not all(isinstance(value, str) for value in item["tags"]) or not isinstance(item["installable"], bool):
                raise ValidationError("invalid-marketplace", "Marketplace catalog entry is invalid.")
            catalog.append(item)
        return {"schema_version": _SCHEMA_VERSION, "online_enabled": raw["online_enabled"], "catalog": catalog}

    def status(self) -> dict[str, Any]:
        data = self._load()
        return {"online_enabled": data["online_enabled"], "catalog_items": len(data["catalog"]), "message": "Online catalog refresh requires explicit enablement; only trusted sources can be installed automatically."}

    def catalog(self, query: object = "") -> dict[str, Any]:
        if not isinstance(query, str) or len(query) > 120:
            raise ValidationError("invalid-marketplace-query", "Marketplace search query is invalid.")
        needle = query.casefold().strip()
        items = self._load()["catalog"]
        if needle:
            items = [item for item in items if needle in " ".join([item["name"], item["description"], *item["tags"]]).casefold()]
        return {"items": sorted(items, key=lambda item: (item["trust"] != "trusted", item["risk_level"], item["name"].casefold()))}

    def recommendations(self) -> dict[str, Any]:
        items = self._load()["catalog"]
        ranked = sorted(items, key=lambda item: (item["trust"] != "trusted", item["risk_level"], item["kind"], item["name"].casefold()))
        return {"items": ranked[:12], "method": "Deterministic ranking by trust, declared risk, type, and name."}
