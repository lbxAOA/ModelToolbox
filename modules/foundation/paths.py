"""Application path resolution and containment checks."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .errors import PathPolicyError


HOME_VARIABLE = "MODELTOOLBOX_NEXT_HOME"


@dataclass(frozen=True)
class AppPaths:
    home: Path
    config_file: Path
    state_dir: Path
    log_dir: Path


def resolve_app_paths(
    home: Path | None = None, environ: Mapping[str, str] | None = None
) -> AppPaths:
    environment = os.environ if environ is None else environ
    selected = home or Path(environment.get(HOME_VARIABLE, Path.home() / ".modeltoolbox-next"))
    resolved = selected.expanduser().resolve()
    return AppPaths(
        home=resolved,
        config_file=resolved / "config.json",
        state_dir=resolved / "state",
        log_dir=resolved / "logs",
    )


def require_within(root: Path, candidate: Path) -> Path:
    resolved_root = root.expanduser().resolve()
    resolved_candidate = candidate.expanduser().resolve()
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as error:
        raise PathPolicyError("path-outside-home", "Path is outside the application home directory.") from error
    return resolved_candidate
