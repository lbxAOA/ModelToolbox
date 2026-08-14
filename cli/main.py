"""ModelToolbox Next command-line application."""

from __future__ import annotations

import os
import sys
from io import TextIOBase
from pathlib import Path
from typing import Mapping, Sequence

from modules.command.model import Command, CommandContext, CommandResult, Option
from modules.command.parser import parse_command
from modules.command.registry import CommandRegistry
from modules.command.render import render_help, render_result
from modules.foundation.config import load_config
from modules.foundation.errors import CommandError, MtbError
from modules.foundation.logging import Logger
from modules.foundation.paths import resolve_app_paths
from modules.protocol.bridge import PROTOCOL, serve as serve_bridge
from modules.ui.service import get_state_value, set_state_value

VERSION = "0.1.0"


def build_registry() -> CommandRegistry:
    registry = CommandRegistry()

    def version(_: CommandContext, __: Mapping[str, object]) -> CommandResult:
        return CommandResult(data={"name": "modeltoolbox-next", "version": VERSION}, message=VERSION)

    def config_show(context: CommandContext, _: Mapping[str, object]) -> CommandResult:
        data = {"home": str(context.paths.home), "output_format": context.config.output_format, "log_level": context.config.log_level}
        return CommandResult(data=data, message=f"home: {data['home']}\noutput_format: {data['output_format']}\nlog_level: {data['log_level']}")

    def state_get(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        key = str(values["key"])
        value = get_state_value(context.paths.state_dir, key)
        return CommandResult(data={"key": key, "value": value}, message=str(value))

    def state_set(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        import json
        key = str(values["key"])
        try:
            value = json.loads(str(values["value"]))
        except json.JSONDecodeError as error:
            raise CommandError("invalid-json-value", "State value must be valid JSON.") from error
        stored = set_state_value(context.paths.state_dir, key, value)
        return CommandResult(data={"key": key, "value": stored}, message=f"Stored: {key}")

    def bridge(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        if values.get("protocol") != PROTOCOL:
            raise CommandError("unsupported-protocol", f"Bridge requires --protocol {PROTOCOL}.")
        serve_bridge(context.stdin, context.stdout, context.paths.state_dir, VERSION)
        return CommandResult()

    registry.register(Command("version", "Show the application version.", version))
    registry.register(Command("config", "Show active local configuration.", config_show))
    registry.register(Command("state-get", "Read a value from local state.", state_get, arguments=("key",)))
    registry.register(Command("state-set", "Write a JSON value to local state.", state_set, arguments=("key", "value")))
    registry.register(Command("bridge", "Run the local presentation-client bridge.", bridge, options=(Option("protocol", takes_value=True, required=True, summary="Protocol version."),)))
    return registry


def main(
    argv: Sequence[str] | None = None,
    *,
    stdin: TextIOBase = sys.stdin,
    stdout: TextIOBase = sys.stdout,
    stderr: TextIOBase = sys.stderr,
    environ: Mapping[str, str] | None = None,
) -> int:
    tokens = list(sys.argv[1:] if argv is None else argv)
    environment = os.environ if environ is None else environ
    output_format = "json" if "--json" in tokens else "text"
    tokens = [token for token in tokens if token != "--json"]
    registry = build_registry()
    if not tokens or tokens == ["--help"]:
        stdout.write(render_help(registry))
        return 0
    command_name = tokens.pop(0)
    if command_name == "help":
        command = registry.get(tokens[0]) if tokens else None
        if tokens and command is None:
            stderr.write(f"Unknown command: {tokens[0]}\n")
            return 2
        stdout.write(render_help(registry, command))
        return 0
    command = registry.get(command_name)
    if command is None:
        stderr.write(f"Unknown command: {command_name}. Use 'mtb help'.\n")
        return 2
    if tokens == ["--help"]:
        stdout.write(render_help(registry, command))
        return 0
    try:
        paths = resolve_app_paths(Path(environment["MODELTOOLBOX_NEXT_HOME"]) if "MODELTOOLBOX_NEXT_HOME" in environment else None, environment)
        config = load_config(paths.config_file, environment, {"output_format": output_format})
        context = CommandContext(paths, config, stdin, stdout, stderr, Logger(stderr, config.log_level))
        parsed = parse_command(command, tokens)
        result = command.handler(context, parsed.values)
        render_result(result, output_format, stdout)
        return result.exit_code
    except CommandError as error:
        stderr.write(f"Error [{error.code}]: {error.message}\n")
        return 2
    except MtbError as error:
        stderr.write(f"Error [{error.code}]: {error.message}\n")
        return 3
    except Exception:
        stderr.write("Error [internal]: Unexpected internal failure.\n")
        return 70


if __name__ == "__main__":
    sys.exit(main())
