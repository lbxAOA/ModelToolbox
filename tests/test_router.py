"""Focused tests for revision-bound router policies and listener lifecycle."""

from __future__ import annotations

import tempfile
from pathlib import Path

from modules.foundation.errors import ValidationError
from modules.profiles.service import ProfileService
from modules.router.policy import RouterPolicyService
from modules.router.runtime import RouterRuntimeService


def _services() -> tuple[tempfile.TemporaryDirectory[str], Path, RouterPolicyService]:
    temporary = tempfile.TemporaryDirectory()
    state = Path(temporary.name) / "state"
    ProfileService(state).create({"id": "work", "name": "Work", "adapter_id": "claude-code", "base_url": "https://gateway.example.test/v1", "model": None, "credential_source": None})
    return temporary, state, RouterPolicyService(state)


def test_router_plan_and_activation_require_current_revision() -> None:
    temporary, _, router = _services()
    try:
        plan = router.plan_activate("work", "anthropic", "openai")
        assert plan["revision"] == 0
        assert plan["ready"]
        active = router.activate("work", "anthropic", "openai", plan["revision"])
        assert active["revision"] == 1
        try:
            router.direct(0)
        except ValidationError as error:
            assert error.code == "router-policy-changed"
        else:
            raise AssertionError("Expected stale revision failure")
    finally:
        temporary.cleanup()


def test_router_direct_and_rollback_use_expected_revision() -> None:
    temporary, _, router = _services()
    try:
        active = router.activate("work", "anthropic", "openai", 0)
        direct = router.direct(active["revision"])
        assert direct["state"] == "direct"
        restored = router.rollback(direct["revision"])
        assert restored["state"] == "active"
        assert restored["active"]["profile_id"] == "work"
    finally:
        temporary.cleanup()


def test_runtime_rejects_non_loopback_and_stops() -> None:
    temporary, state, router = _services()
    try:
        runtime = RouterRuntimeService(state, router)
        try:
            runtime.start("0.0.0.0", 15721)
        except ValidationError as error:
            assert error.code == "router-bind-rejected"
        else:
            raise AssertionError("Expected loopback validation failure")
        status = runtime.start("127.0.0.1", 15729)
        assert status["running"]
        assert runtime.stop()["running"] is False
    finally:
        temporary.cleanup()
