from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Sequence

from modeltoolbox_core.paths import resolve_in_root
from modeltoolbox_core.proc import ProcessResult, run_command

from .audit import write_audit_record
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
    "reboot",
    "halt",
    "sudo",
    "su",
}
BLOCKED_TOKENS = {
    "--no-preserve-root",
    "-rf",
    "-fr",
    "/s",
    "/q",
    "/f",
}


def run_in_env(
    name: str,
    args: Sequence[str],
    *,
    project_root: Path | None = None,
    cwd: Path | str | None = None,
    timeout: float = 120,
    network: bool = True,
    memory_mb: int | None = None,
    cpu_cores: int | None = None,
) -> ProcessResult:
    """Execute a command in a sandbox environment.
    
    Args:
        name: Environment name
        args: Command and arguments
        project_root: Optional project root
        cwd: Working directory (relative to workspace)
        timeout: Execution timeout in seconds
        network: Allow network access
        memory_mb: Memory limit in MB (not implemented on Windows)
        cpu_cores: CPU core limit (not implemented on Windows)
        
    Returns:
        Process execution result
    """
    if not args:
        raise ValueError("Command is required")
    _validate_command(args)
    env = create_env(name, project_root=project_root)
    workdir = _resolve_workspace_cwd(env, cwd)
    env_vars = _build_env(env, network=network)
    
    start_time = time.time()
    result = run_command(list(args), cwd=workdir, env=env_vars, timeout=timeout)
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Write audit log
    write_audit_record(
        env_name=name,
        command=list(args),
        cwd=workdir,
        exit_code=result.returncode,
        duration_ms=duration_ms,
        stdout=result.stdout,
        stderr=result.stderr,
        network_allowed=network,
        timeout=timeout,
        project_root=project_root,
    )
    
    return result


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