"""Standard-library foundation primitives for ModelToolbox Next."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any
from .errors import StorageError


class FoundationError(StorageError):
    """Backward-compatible storage failure alias."""

    def __init__(self, message: str) -> None:
        super().__init__("storage-failure", message)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise FoundationError(f"Cannot read JSON state from {path}") from error


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temporary_path.replace(path)
    except OSError as error:
        raise FoundationError(f"Cannot write JSON state to {path}") from error
    finally:
        if temporary_path.exists():
            temporary_path.unlink(missing_ok=True)
