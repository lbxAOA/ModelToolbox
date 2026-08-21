"""Focused tests for non-secret configuration profiles."""

from __future__ import annotations

import tempfile
from pathlib import Path

from modules.foundation.errors import ValidationError
from modules.profiles.service import ProfileService


def _service() -> tuple[tempfile.TemporaryDirectory[str], Path, ProfileService]:
    temporary = tempfile.TemporaryDirectory()
    home = Path(temporary.name)
    return temporary, home, ProfileService(home / "state", {"HOME": str(home)})


def _create(service: ProfileService, adapter_id: str = "claude-code") -> dict[str, object]:
    return service.create({
        "id": "work",
        "name": "Work Gateway",
        "adapter_id": adapter_id,
        "base_url": "https://gateway.example.test/v1",
        "model": "example-model",
        "credential_source": "WORK_GATEWAY_KEY",
    })


def test_profile_summary_does_not_expose_credential_source() -> None:
    temporary, _, service = _service()
    try:
        summary = _create(service)
        assert "credential_source" not in summary
        assert summary["credential_status"] == "not-managed"
        assert service.list()["profiles"][0]["id"] == "work"
    finally:
        temporary.cleanup()


def test_rejects_non_loopback_http_url() -> None:
    temporary, _, service = _service()
    try:
        try:
            service.create({"id": "insecure", "name": "Insecure", "adapter_id": "claude-code", "base_url": "http://example.test", "model": None, "credential_source": None})
        except ValidationError as error:
            assert error.code == "insecure-base-url"
        else:
            raise AssertionError("Expected insecure URL validation failure")
    finally:
        temporary.cleanup()


def test_select_does_not_apply_external_configuration() -> None:
    temporary, home, service = _service()
    try:
        _create(service)
        service.select("work")
        assert service.list()["selected_profile_id"] == "work"
        assert not (home / ".claude/settings.json").exists()
    finally:
        temporary.cleanup()


def test_claude_plan_and_apply_preserve_unmanaged_fields() -> None:
    temporary, home, service = _service()
    try:
        _create(service)
        target = home / ".claude/settings.json"
        target.parent.mkdir()
        target.write_text('{"permissions":{"allow":["Read"]},"env":{"OTHER":"unchanged"}}\n', encoding="utf-8")
        plan = service.plan_apply("work")
        assert plan["ready"]
        result = service.apply("work", plan["revision"])
        assert result["applied"]
        stored = target.read_text(encoding="utf-8")
        assert '"OTHER": "unchanged"' in stored
        assert '"ANTHROPIC_BASE_URL": "https://gateway.example.test/v1"' in stored
        assert "WORK_GATEWAY_KEY" not in stored
        assert target.with_suffix(".json.modeltoolbox-backup").exists()
    finally:
        temporary.cleanup()


def test_pending_adapters_are_visible_and_cannot_touch_files() -> None:
    for adapter_id in ("codex-cli", "codex-desktop", "claude-desktop"):
        temporary, home, service = _service()
        try:
            _create(service, adapter_id)
            inspection = service.inspect("work")
            assert inspection["status"] == "unavailable"
            plan = service.plan_apply("work")
            assert not plan["ready"]
            assert plan["revision"] is None
            try:
                service.apply("work", "0" * 64)
            except ValidationError as error:
                assert error.code == "adapter-unavailable"
            else:
                raise AssertionError("Expected unavailable adapter failure")
            assert not (home / ".claude").exists()
            assert not (home / ".codex").exists()
        finally:
            temporary.cleanup()


def test_adapter_catalog_only_enables_claude_code() -> None:
    temporary, _, service = _service()
    try:
        adapters = {item["id"]: item for item in service.list_adapters()["adapters"]}
        assert set(adapters) == {"claude-code", "codex-cli", "codex-desktop", "claude-desktop"}
        assert adapters["claude-code"]["write_enabled"]
        assert all(not adapters[item]["write_enabled"] for item in ("codex-cli", "codex-desktop", "claude-desktop"))
    finally:
        temporary.cleanup()


def test_apply_rejects_stale_revision() -> None:
    temporary, home, service = _service()
    try:
        _create(service)
        target = home / ".claude/settings.json"
        target.parent.mkdir()
        target.write_text('{"env":{}}', encoding="utf-8")
        plan = service.plan_apply("work")
        target.write_text('{"env":{"OTHER":"changed"}}', encoding="utf-8")
        try:
            service.apply("work", plan["revision"])
        except ValidationError as error:
            assert error.code == "target-config-changed"
        else:
            raise AssertionError("Expected stale revision failure")
    finally:
        temporary.cleanup()


def test_clearing_profile_model_removes_only_managed_model() -> None:
    temporary, home, service = _service()
    try:
        _create(service)
        target = home / ".claude/settings.json"
        target.parent.mkdir()
        target.write_text('{"env":{"ANTHROPIC_MODEL":"old-model","OTHER":"unchanged"}}', encoding="utf-8")
        service.update("work", {"name": "Work Gateway", "base_url": "https://gateway.example.test/v1", "model": None, "credential_source": None})
        plan = service.plan_apply("work")
        assert {change["field"] for change in plan["changes"]} == {"base_url", "model"}
        service.apply("work", plan["revision"])
        stored = target.read_text(encoding="utf-8")
        assert "ANTHROPIC_MODEL" not in stored
        assert '"OTHER": "unchanged"' in stored
    finally:
        temporary.cleanup()


def test_profile_update_preserves_adapter_and_redacts_credential_source() -> None:
    temporary, _, service = _service()
    try:
        _create(service)
        updated = service.update("work", {"name": "Updated", "base_url": "https://updated.example.test/v1", "model": None, "credential_source": "UPDATED_KEY"})
        assert updated["name"] == "Updated"
        assert updated["adapter_id"] == "claude-code"
        assert "credential_source" not in updated
    finally:
        temporary.cleanup()
