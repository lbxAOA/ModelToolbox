"""First-party error types for ModelToolbox Next."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(eq=False)
class MtbError(Exception):
    """A user-safe error with a stable machine-readable code."""

    code: str
    message: str
    detail: str | None = None

    def __str__(self) -> str:
        return self.message


class FoundationError(MtbError):
    """Base error raised by foundation services."""


class ValidationError(FoundationError):
    """Input did not meet an application contract."""


class PathPolicyError(FoundationError):
    """A path falls outside an allowed application boundary."""


class StorageError(FoundationError):
    """State could not be read or written safely."""


class ProcessError(FoundationError):
    """A local process could not be started or completed."""


class CommandError(MtbError):
    """A command could not be registered, parsed, or executed."""
