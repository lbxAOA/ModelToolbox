from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CoreConfig:
    root: Path
    state_dir: Path
    cache_dir: Path


def default_config(root: Path | None = None) -> CoreConfig:
    project_root = (root or Path.cwd()).resolve()
    state_dir = project_root / ".modeltoolbox"
    return CoreConfig(root=project_root, state_dir=state_dir, cache_dir=state_dir / "cache")


def get_state_dir(root: Path | None = None) -> Path:
    """Get the state directory path."""
    return default_config(root).state_dir
