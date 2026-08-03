from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from modeltoolbox_core.proc import ProcessResult, run_command


@dataclass(frozen=True)
class RuntimeSpec:
    name: str
    executable: str
    available: bool
    path: str | None


RUNTIME_EXECUTABLES = {
    "copilot": "copilot",
    "claude": "claude",
    "codex": "codex",
    "aider": "aider",
}


def available_runtimes() -> list[RuntimeSpec]:
    runtimes = []
    for name, executable in RUNTIME_EXECUTABLES.items():
        path = shutil.which(executable)
        runtimes.append(
            RuntimeSpec(
                name=name,
                executable=executable,
                available=path is not None,
                path=path,
            )
        )
    return runtimes


def run_runtime(
    name: str,
    args: list[str],
    *,
    cwd: Path | None = None,
    timeout: float = 300.0,
) -> ProcessResult:
    executable = RUNTIME_EXECUTABLES.get(name)
    if executable is None:
        raise ValueError(f"Unknown runtime: {name}")
    return run_command([executable, *args], cwd=cwd, timeout=timeout)