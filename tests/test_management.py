"""Tests for guarded integration, MCP, Skill, and marketplace foundations."""

from __future__ import annotations

import tempfile
from pathlib import Path

from modules.foundation.errors import ValidationError
from modules.integrations.service import IntegrationService
from modules.marketplace.service import MarketplaceService
from modules.mcp.service import McpService
from modules.protocol.bridge import BridgeRequest, dispatch
from modules.skill.service import SkillService


def _temporary_path() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temporary = tempfile.TemporaryDirectory()
    return temporary, Path(temporary.name)


def _assert_validation(action, expected_message: str) -> None:
    try:
        action()
    except ValidationError as error:
        assert expected_message in error.message
    else:
        raise AssertionError("Expected validation failure")


def test_integrations_expose_verified_and_export_only_contracts() -> None:
    temporary, path = _temporary_path()
    try:
        data = IntegrationService({"HOME": str(path)}).list()
        adapters = {item["id"]: item for item in data["adapters"]}
        assert adapters["claude-code"]["write_enabled"] is True
        assert adapters["cursor"]["write_enabled"] is False
        assert adapters["generic-export"]["contract_status"] == "export-only"
    finally:
        temporary.cleanup()


def test_mcp_rejects_shell_strings_and_secret_values() -> None:
    temporary, path = _temporary_path()
    try:
        service = McpService(path)
        _assert_validation(
            lambda: service.register({"id": "bad", "name": "Bad", "transport": "stdio", "url": None, "command": "python server.py", "cwd": str(path), "environment": [], "risk_level": "high"}),
            "string array",
        )
        _assert_validation(
            lambda: service.register({"id": "bad", "name": "Bad", "transport": "stdio", "url": None, "command": ["python", "server.py"], "cwd": str(path), "environment": ["secret-value"], "risk_level": "high"}),
            "environment variable names",
        )
    finally:
        temporary.cleanup()


def test_mcp_registration_is_disabled_until_explicitly_enabled() -> None:
    temporary, path = _temporary_path()
    try:
        service = McpService(path)
        registered = service.register({"id": "local-tools", "name": "Local tools", "transport": "stdio", "url": None, "command": ["python", "server.py"], "cwd": str(path), "environment": ["LOCAL_TOOLS_TOKEN"], "risk_level": "high"})
        assert registered["enabled"] is False
        enabled = service.set_enabled("local-tools", True)
        assert enabled["enabled"] is True
        assert enabled["environment_names"] == ["LOCAL_TOOLS_TOKEN"]
    finally:
        temporary.cleanup()


def test_marketplace_defaults_to_offline_empty_cache() -> None:
    temporary, path = _temporary_path()
    try:
        service = MarketplaceService(path)
        assert service.status()["online_enabled"] is False
        assert service.catalog()["items"] == []
        assert service.recommendations()["items"] == []
    finally:
        temporary.cleanup()


def test_skill_removal_requires_existing_managed_record() -> None:
    temporary, path = _temporary_path()
    try:
        _assert_validation(lambda: SkillService(path).remove("missing-skill"), "Skill was not found")
    finally:
        temporary.cleanup()


def test_bridge_rejects_unknown_marketplace_payload() -> None:
    temporary, path = _temporary_path()
    try:
        request = BridgeRequest("request-1", "marketplace.status", {"unexpected": True})
        _assert_validation(lambda: dispatch(request, path, "test"), "does not accept")
    finally:
        temporary.cleanup()


def test_bridge_exposes_management_operations() -> None:
    temporary, path = _temporary_path()
    try:
        request = BridgeRequest("request-1", "bridge.info", {})
        data = dispatch(request, path, "test")["data"]
        assert "mcp.start" in data["operations"]
        assert "marketplace.recommendations" in data["operations"]
    finally:
        temporary.cleanup()
