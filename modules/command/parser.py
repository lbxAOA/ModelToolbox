"""Strict token parsing for first-party commands."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from .model import Command
from modules.foundation.errors import CommandError


@dataclass(frozen=True)
class ParsedCommand:
    command: Command
    values: dict[str, Any]


def parse_command(command: Command, tokens: Sequence[str]) -> ParsedCommand:
    options = {option.name: option for option in command.options}
    values: dict[str, Any] = {option.name: False for option in command.options if not option.takes_value}
    positionals: list[str] = []
    index = 0
    positional_only = False
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            positional_only = True
            index += 1
            continue
        if not positional_only and token.startswith("--"):
            name, separator, inline_value = token[2:].partition("=")
            option = options.get(name)
            if option is None:
                raise CommandError("unknown-option", f"Unknown option: --{name}")
            if option.takes_value:
                if separator:
                    value = inline_value
                else:
                    index += 1
                    if index >= len(tokens):
                        raise CommandError("missing-option-value", f"Option needs a value: --{name}")
                    value = tokens[index]
                values[name] = value
            elif separator:
                raise CommandError("unexpected-option-value", f"Flag does not take a value: --{name}")
            else:
                values[name] = True
        else:
            positionals.append(token)
        index += 1
    if len(positionals) != len(command.arguments):
        raise CommandError("invalid-arguments", f"Usage: {command.name} {' '.join(command.arguments)}".rstrip())
    values.update(zip(command.arguments, positionals, strict=True))
    for option in command.options:
        if option.required and option.name not in values:
            raise CommandError("missing-option", f"Required option missing: --{option.name}")
    return ParsedCommand(command, values)
