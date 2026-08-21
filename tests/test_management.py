"""Tests for guarded integration, MCP, Skill, and marketplace foundations."""

from __future__ import annotations

from pathlib import Path

import pytest

from modules.foundation.errors import ValidationError
from modules.integrations.service import IntegrationService
from modules.marketplace.service import MarketplaceService
from modules.mcp.service import McpService
from modules.protocol.bridge import BridgeRequest, dispatch
from modules.skill.service import SkillService


def test_integrations_expose_verified_and_export_only_contracts(tmp_path: Path) -> None:
    data = IntegrationService({"HOME": str(tmp_path)}).list()
    adapters = {item["id"]: item for item in data["adapters"]}
    assert adapters["claude-code"]["write_enabled"] is True
    assert adapters["cursor"]["write_enabled"] is False
    assert adapters["generic-export"]["contract_status"] == "export-only"


def test_mcp_rejects_shell_strings_and_secret_values(tmp_path: Path) -> None:
    service = McpService(tmp_path)
    with pytest.raises(ValidationError, match="string array"):
        service.register({"id": "bad", "name": "Bad", "transport": "stdio", "url": None, "command": "python server.py", "cwd": str(tmp_path), "environment": [], "risk_level": "high"})
    with pytest.raises(ValidationError, match="environment variable names"):
        service.register({"id": "bad", "name": "Bad", "transport": "stdio", "url": None, "command": ["python", "server.py"], "cwd": str(tmp_path), "environment": ["secret-value"], "risk_level": "high"})


def test_mcp_registration_is_disabled_until_explicitly_enabled(tmp_path: Path) -> None:
    service = McpService(tmp_path)
    registered = service.register({"id": "local-tools", "name": "Local tools", "transport": "stdio", "url": None, "command": ["python", "server.py"], "cwd": str(tmp_path), "environment": ["LOCAL_TOOLS_TOKEN"], "risk_level": "high"})
    assert registered["enabled"] is False
    enabled = service.set_enabled("local-tools", True)
    assert enabled["enabled"] is True
    assert enabled["environment_names"] == ["LOCAL_TOOLS_TOKEN"]


def test_marketplace_defaults_to_offline_empty_cache(tmp_path: Path) -> None:
    service = MarketplaceService(tmp_path)
    assert service.status()["online_enabled"] is False
    assert service.catalog()["items"] == []
    assert service.recommendations()["items"] == []


def test_skill_removal_requires_existing_managed_record(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="Skill was not found"):
        SkillService(tmp_path).remove("missing-skill")


def test_bridge_rejects_unknown_marketplace_payload(tmp_path: Path) -> None:
    request = BridgeRequest("request-1", "marketplace.status", {"unexpected": True})
    with pytest.raises(ValidationError, match="does not accept"):
        dispatch(request, tmp_path, "test")


def test_bridge_exposes_management_operations(tmp_path: Path) -> None:
    request = BridgeRequest("request-1", "bridge.info", {})
    data = dispatch(request, tmp_path, "test")["data"]
    assert "mcp.start" in data["operations"]
    assert "marketplace.recommendations" in data["operations"]
