"""Deterministic command registration."""

from __future__ import annotations

from .model import Command
from modules.foundation.errors import CommandError


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        if command.name in self._commands:
            raise CommandError("duplicate-command", f"Command already registered: {command.name}")
        self._commands[command.name] = command

    def get(self, name: str) -> Command | None:
        return self._commands.get(name)

    def all(self) -> tuple[Command, ...]:
        return tuple(self._commands[name] for name in sorted(self._commands))
