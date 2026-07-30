from __future__ import annotations

import shlex
from collections.abc import Sequence

import click
import typer


EXIT_COMMANDS = {"exit", "quit", "q"}
HELP_COMMANDS = {"help", "?"}
CLEAR_COMMANDS = {"clear", "cls"}


def run_shell(app: typer.Typer) -> None:
    """Run the terminal-first ModelToolbox prompt."""
    typer.echo("ModelToolbox terminal")
    typer.echo("Type help for commands, or exit to quit.")
    while True:
        try:
            line = typer.prompt("mtb", prompt_suffix="> ").lstrip("\ufeff").strip()
        except (EOFError, KeyboardInterrupt):
            typer.echo()
            return

        if not line:
            continue

        lowered = line.lower()
        if lowered in EXIT_COMMANDS:
            return
        if lowered in HELP_COMMANDS:
            _invoke(app, ["--help"])
            continue
        if lowered in CLEAR_COMMANDS:
            typer.echo("\033c", nl=False)
            continue

        try:
            argv = shlex.split(line)
        except ValueError as exc:
            typer.secho(f"parse error: {exc}", fg=typer.colors.RED)
            continue

        _invoke(app, argv)


def _invoke(app: typer.Typer, argv: Sequence[str]) -> None:
    try:
        app(args=list(argv), standalone_mode=False)
    except click.exceptions.Exit as exc:
        if exc.exit_code not in (0, None):
            typer.secho(f"exit code: {exc.exit_code}", fg=typer.colors.RED)
    except click.ClickException as exc:
        exc.show()
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        if code:
            typer.secho(f"exit code: {code}", fg=typer.colors.RED)
