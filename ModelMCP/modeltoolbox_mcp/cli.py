from __future__ import annotations

from dataclasses import asdict

import typer

from modeltoolbox_core.jsonio import dump_json

from .registry import (
    McpServer,
    discover_servers,
    export_config,
    list_servers,
    remove_server,
    scaffold_server,
    upsert_server,
)

app = typer.Typer(help="Manage MCP server scaffolds, registry, lifecycle, and exports.")


def register(root: typer.Typer) -> None:
    root.add_typer(app, name="mcp")


@app.command()
def doctor() -> None:
    typer.echo(f"mcp: registered servers={len(list_servers())}")


@app.command("discover")
def discover_command(
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    servers = discover_servers()
    if json_output:
        dump_json({"servers": [asdict(server) for server in servers]})
        return
    typer.echo(f"discovered={len(servers)}")


@app.command("list")
def list_command(
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    servers = list_servers()
    if json_output:
        dump_json({"servers": [asdict(server) for server in servers]})
        return
    for server in servers:
        typer.echo(f"{server.name}\t{' '.join(server.command)}")


@app.command("add")
def add_command(
    name: str = typer.Argument(..., help="Server name."),
    command: list[str] = typer.Argument(..., help="Command argv used to start the server."),
    cwd: str | None = typer.Option(None, "--cwd", help="Working directory."),
    description: str = typer.Option("", "--description", help="Registry description."),
) -> None:
    upsert_server(McpServer(name=name, command=command, cwd=cwd, description=description))
    typer.echo(name)


@app.command("remove")
def remove_command(name: str = typer.Argument(..., help="Server name.")) -> None:
    if not remove_server(name):
        typer.echo(f"No MCP server named {name}", err=True)
        raise typer.Exit(1)
    typer.echo(name)


@app.command("export")
def export_command() -> None:
    dump_json(export_config(), pretty=True)


@app.command("scaffold")
def scaffold_command(
    name: str = typer.Argument(..., help="Server scaffold name."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Replace an existing scaffold."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    try:
        path = scaffold_server(name, overwrite=overwrite)
    except (FileExistsError, ValueError) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error
    if json_output:
        dump_json({"server": str(path)})
        return
    typer.echo(path)
