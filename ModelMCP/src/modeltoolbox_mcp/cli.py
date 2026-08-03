from __future__ import annotations

from dataclasses import asdict

import typer

from modeltoolbox_core.jsonio import dump_json
from modeltoolbox_core.logging import get_logger
from modeltoolbox_core.telemetry import track_performance

from .registry import (
    McpServer,
    discover_servers,
    export_config,
    list_servers,
    remove_server,
    scaffold_server,
    upsert_server,
)

logger = get_logger(__name__)
app = typer.Typer(help="Manage MCP server scaffolds, registry, lifecycle, and exports.")


def register(root: typer.Typer) -> None:
    root.add_typer(app, name="mcp")


@app.command()
@track_performance
def doctor() -> None:
    server_count = len(list_servers())
    logger.info(f"MCP doctor check: {server_count} registered servers")
    typer.echo(f"mcp: registered servers={server_count}")


@app.command("discover")
@track_performance
def discover_command(
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    servers = discover_servers()
    logger.info(f"Discovered {len(servers)} MCP servers")
    if json_output:
        dump_json({"servers": [asdict(server) for server in servers]})
        return
    typer.echo(f"discovered={len(servers)}")


@app.command("list")
@track_performance
def list_command(
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    servers = list_servers()
    logger.info(f"Listing {len(servers)} MCP servers")
    if json_output:
        dump_json({"servers": [asdict(server) for server in servers]})
        return
    for server in servers:
        typer.echo(f"{server.name}\t{' '.join(server.command)}")


@app.command("add")
@track_performance
def add_command(
    name: str = typer.Argument(..., help="Server name."),
    command: list[str] = typer.Argument(..., help="Command argv used to start the server."),
    cwd: str | None = typer.Option(None, "--cwd", help="Working directory."),
    description: str = typer.Option("", "--description", help="Registry description."),
) -> None:
    upsert_server(McpServer(name=name, command=command, cwd=cwd, description=description))
    logger.info(f"Added MCP server: {name}")
    typer.echo(name)


@app.command("remove")
@track_performance
def remove_command(name: str = typer.Argument(..., help="Server name.")) -> None:
    if not remove_server(name):
        logger.warning(f"MCP server not found: {name}")
        typer.echo(f"No MCP server named {name}", err=True)
        raise typer.Exit(1)
    logger.info(f"Removed MCP server: {name}")
    typer.echo(name)


@app.command("export")
@track_performance
def export_command() -> None:
    logger.info("Exporting MCP configuration")
    dump_json(export_config(), pretty=True)


@app.command("scaffold")
@track_performance
def scaffold_command(
    name: str = typer.Argument(..., help="Server scaffold name."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Replace an existing scaffold."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    try:
        path = scaffold_server(name, overwrite=overwrite)
        logger.info(f"Scaffolded MCP server: {name} at {path}")
    except (FileExistsError, ValueError) as error:
        logger.error(f"Scaffold failed for {name}: {error}")
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error
    if json_output:
        dump_json({"server": str(path)})
        return
    typer.echo(path)
