from __future__ import annotations

from pathlib import Path


def resolve_in_root(root: Path, target: Path | str) -> Path:
    root_path = root.resolve()
    resolved = (root_path / target).resolve() if not Path(target).is_absolute() else Path(target).resolve()
    if resolved != root_path and root_path not in resolved.parents:
        raise ValueError(f"Path escapes root: {resolved}")
    return resolved
