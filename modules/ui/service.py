"""Validated UI state access through Foundation storage."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from modules.foundation.errors import ValidationError
from modules.foundation.storage import read_json, write_json_atomic
from .model import ViewSnapshot, snapshot_from_state

_KEY = re.compile(r"[a-z][a-z0-9_.-]{0,63}\Z")


def state_path(state_dir: Path) -> Path:
    return state_dir / "state.json"


def validate_key(key: object) -> str:
    if not isinstance(key, str) or not _KEY.fullmatch(key):
        raise ValidationError("invalid-state-key", "State key must be a lower-case identifier.")
    return key


def validate_value(value: Any) -> Any:
    try:
        json.dumps(value, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValidationError("invalid-state-value", "State value must be JSON-compatible.") from error
    return value


def load_state(state_dir: Path) -> dict[str, Any]:
    state = read_json(state_path(state_dir), {})
    if not isinstance(state, dict) or not all(isinstance(key, str) for key in state):
        raise ValidationError("invalid-state", "Stored state must be a JSON object with string keys.")
    return state


def get_state_value(state_dir: Path, key: object) -> Any:
    safe_key = validate_key(key)
    state = load_state(state_dir)
    if safe_key not in state:
        raise ValidationError("state-key-missing", "State key was not found.")
    return state[safe_key]


def set_state_value(state_dir: Path, key: object, value: Any) -> Any:
    safe_key = validate_key(key)
    safe_value = validate_value(value)
    state = load_state(state_dir)
    state[safe_key] = safe_value
    write_json_atomic(state_path(state_dir), state)
    return safe_value


def load_snapshot(state_dir: Path, version: str) -> ViewSnapshot:
    return snapshot_from_state(version, load_state(state_dir))
