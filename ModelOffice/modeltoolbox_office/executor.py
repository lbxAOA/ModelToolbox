from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

from modeltoolbox_core.paths import resolve_in_root
from modeltoolbox_core.proc import ProcessResult, run_command

from .envs import OfficeEnv, create_env


BLOCKED_COMMANDS = {
    "del",
    "erase",
    "format",
    "mkfs",
    "rm",
    "rmdir",
    "remove-item",
    "rd",
    "shutdown",
}
BLOCKED_TOKENS = {
    "--no-preserve-root",
    "-rf",
    "-fr",
    "/s",
    "/q",
}


def run_in_env(
    name: str,
    args: Sequence[str],
    *,
    project_root: Path | None = None,
    cwd: Path | str | None = None,
    timeout: float = 120,
    network: bool = True,
) -> ProcessResult:
    if not args:
        raise ValueError("Command is required")
    _validate_command(args)
    env = create_env(name, project_root=project_root)
    workdir = _resolve_workspace_cwd(env, cwd)
    env_vars = _build_env(env, network=network)
    return run_command(list(args), cwd=workdir, env=env_vars, timeout=timeout)


def _resolve_workspace_cwd(env: OfficeEnv, cwd: Path | str | None) -> Path:
    if cwd is None:
        env.workspace.mkdir(parents=True, exist_ok=True)
        return env.workspace
    resolved = resolve_in_root(env.workspace, cwd)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _validate_command(args: Sequence[str]) -> None:
    executable = Path(args[0]).name.lower()
    if executable.endswith(".exe"):
        executable = executable[:-4]
    if executable in BLOCKED_COMMANDS:
        raise ValueError(f"Blocked command: {args[0]}")
    lowered = {part.lower() for part in args[1:]}
    blocked = sorted(lowered & BLOCKED_TOKENS)
    if blocked:
        raise ValueError(f"Blocked command token: {blocked[0]}")


def _build_env(env: OfficeEnv, *, network: bool) -> dict[str, str]:
    values = dict(os.environ)
    scripts_dir = env.python.parent
    values["VIRTUAL_ENV"] = str(env.venv)
    values["PATH"] = f"{scripts_dir}{os.pathsep}{values.get('PATH', '')}"
    values["MODELTOOLBOX_OFFICE_WORKSPACE"] = str(env.workspace)
    values["MODELTOOLBOX_OFFICE_NETWORK"] = "1" if network else "0"
    if not network:
        values.setdefault("NO_PROXY", "*")
        values.setdefault("PIP_NO_INDEX", "1")
    return values