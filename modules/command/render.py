"""Plain-text and JSON command output."""

from __future__ import annotations

import json
from typing import TextIO

from .model import Command, CommandResult
from .registry import CommandRegistry


def render_help(registry: CommandRegistry, command: Command | None = None) -> str:
    if command is None:
        lines = ["Usage: mtb [--json] <command> [arguments]", "", "Commands:"]
        lines.extend(f"  {item.name:<12} {item.summary}" for item in registry.all())
        return "\n".join(lines) + "\n"
    usage = f"Usage: mtb {command.name}"
    if command.options:
        usage += " [options]"
    if command.arguments:
        usage += " " + " ".join(f"<{name}>" for name in command.arguments)
    lines = [usage, "", command.summary]
    if command.options:
        lines.extend(["", "Options:"])
        for option in command.options:
            suffix = " <value>" if option.takes_value else ""
            lines.append(f"  --{option.name}{suffix:<12} {option.summary}")
    return "\n".join(lines) + "\n"


def render_result(result: CommandResult, output_format: str, stream: TextIO) -> None:
    if output_format == "json":
        stream.write(json.dumps(result.data or {}, ensure_ascii=False, sort_keys=True) + "\n")
    elif result.message is not None:
        stream.write(result.message + "\n")
