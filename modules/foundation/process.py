"""Bounded local process execution without shell interpolation."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from .errors import ProcessError


@dataclass(frozen=True)
class ProcessResult:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    elapsed_seconds: float


def run_process(
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    environ: Mapping[str, str] | None = None,
    timeout_seconds: float | None = None,
    output_limit: int = 1_000_000,
) -> ProcessResult:
    if not args or any(not isinstance(value, str) or not value for value in args):
        raise ProcessError("invalid-process", "A process requires non-empty literal arguments.")
    started = time.monotonic()
    try:
        completed = subprocess.run(
            list(args), cwd=cwd, env=dict(environ) if environ is not None else None,
            capture_output=True, text=True, shell=False, timeout=timeout_seconds, check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise ProcessError("process-timeout", "Local process exceeded its time limit.") from error
    except OSError as error:
        raise ProcessError("process-start-failed", "Local process could not be started.") from error
    stdout, stderr = completed.stdout[:output_limit], completed.stderr[:output_limit]
    return ProcessResult(tuple(args), completed.returncode, stdout, stderr, time.monotonic() - started)
