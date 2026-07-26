from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


@dataclass(frozen=True)
class ProcessResult:
    args: Sequence[str]
    returncode: int
    stdout: str
    stderr: str


def run_command(
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    timeout: float = 120,
) -> ProcessResult:
    completed = subprocess.run(
        list(args),
        cwd=cwd,
        env=dict(env) if env is not None else None,
        shell=False,
        timeout=timeout,
        capture_output=True,
        text=True,
    )
    return ProcessResult(
        args=tuple(args),
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )


CommandResult = ProcessResult
