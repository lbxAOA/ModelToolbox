"""Command definitions and command execution context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, TextIO

from modules.foundation.config import Config
from modules.foundation.logging import Logger
from modules.foundation.paths import AppPaths


@dataclass(frozen=True)
class CommandContext:
    paths: AppPaths
    config: Config
    stdin: TextIO
    stdout: TextIO
    stderr: TextIO
    logger: Logger


@dataclass(frozen=True)
class CommandResult:
    exit_code: int = 0
    data: Mapping[str, Any] | None = None
    message: str | None = None


@dataclass(frozen=True)
class Option:
    name: str
    takes_value: bool = False
    required: bool = False
    summary: str = ""


Handler = Callable[[CommandContext, Mapping[str, Any]], CommandResult]


@dataclass(frozen=True)
class Command:
    name: str
    summary: str
    handler: Handler
    options: tuple[Option, ...] = ()
    arguments: tuple[str, ...] = ()
