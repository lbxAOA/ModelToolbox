from __future__ import annotations

from importlib import import_module
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
import sys

import typer

from .git_guard import GitDeletionReport, inspect_git_deletions
from .plugin import PluginLoadError, load_plugins
from .shell import run_shell

app = typer.Typer(
    name="mtb",
    help="ModelToolbox terminal control plane.",
    no_args_is_help=False,
)
guard_app = typer.Typer(help="Repository safety checks.", no_args_is_help=True)
BUILTIN_PLUGINS = (
    "modeltoolbox_ingest.cli",
    "modeltoolbox_provider.cli",
    "modeltoolbox_office.cli",
    "modeltoolbox_memory.cli",
    "modeltoolbox_mcp.cli",
    "modeltoolbox_skill.cli",
    "modeltoolbox_training.cli",
)

BUILTIN_PLUGIN_NAMES = {
    "ingest",
    "provider",
    "office",
    "memory",
    "mcp",
    "skill",
    "train",
}


def register(root: typer.Typer) -> None:
    root.add_typer(guard_app, name="guard")


@app.callback(invoke_without_command=True)
def _root(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        run_shell(app)


@app.command()
def doctor() -> None:
    """Report the runtime state needed by the ModelToolbox command."""
    typer.echo("ModelToolbox doctor")
    typer.echo("- core: ok")
    typer.echo(f"- python: {sys.version.split()[0]}")
    typer.echo(f"- cwd: {Path.cwd()}")
    try:
        installed_version = package_version("modeltoolbox")
    except PackageNotFoundError:
        installed_version = "editable checkout"
    typer.echo(f"- package: {installed_version}")


@app.command()
def version() -> None:
    """Print the installed ModelToolbox version."""
    try:
        installed_version = package_version("modeltoolbox")
    except PackageNotFoundError:
        installed_version = "0.1.0"
    typer.echo(f"modeltoolbox {installed_version}")


@guard_app.command("git-deletions")
def guard_git_deletions(
    max_deleted: int = typer.Option(5, help="Maximum tolerated deleted tracked files."),
    repo: Path = typer.Option(Path.cwd(), help="Repository root to inspect."),
) -> None:
    """Fail when too many tracked deletions are staged or present."""
    report = inspect_git_deletions(repo=repo, max_deleted=max_deleted)
    _print_deletion_report(report)
    if not report.allowed:
        raise typer.Exit(2)


def _print_deletion_report(report: GitDeletionReport) -> None:
    typer.echo(f"deleted={report.deleted_count} max={report.max_deleted}")
    for path in report.deleted_paths[:20]:
        typer.echo(f"D {path}")
    if report.deleted_count > 20:
        typer.echo(f"... {report.deleted_count - 20} more")


def main() -> None:
    register(app)
    register_builtins(app)
    try:
        load_plugins(app, skip_names=BUILTIN_PLUGIN_NAMES)
    except PluginLoadError as exc:
        raise typer.BadParameter(str(exc)) from exc
    app()


def register_builtins(root: typer.Typer) -> None:
    for module_name in BUILTIN_PLUGINS:
        module = import_module(module_name)
        module.register(root)


if __name__ == "__main__":
    main()
