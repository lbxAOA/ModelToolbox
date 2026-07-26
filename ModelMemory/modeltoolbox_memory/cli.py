from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import typer

from modeltoolbox_core.jsonio import dump_json

from .index import default_database, impact_candidates, index_directory, search_index

app = typer.Typer(help="Index and query project context to reduce repeated model reads.")


def register(root: typer.Typer) -> None:
    root.add_typer(app, name="memory")


@app.command()
def doctor() -> None:
    typer.echo(f"memory: database={default_database(Path.cwd())}")


@app.command("index")
def index_command(
    root: Path = typer.Argument(Path("."), help="Directory to index."),
    database: Path | None = typer.Option(None, "--db", help="SQLite database path."),
    include: list[str] | None = typer.Option(None, "--include", help="File extension to include, for example .py."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    extensions = {item if item.startswith(".") else f".{item}" for item in include} if include else None
    stats = index_directory(root, database=database, extensions=extensions)
    payload = {
        "root": str(stats.root),
        "database": str(stats.database),
        "indexed": stats.indexed,
        "skipped": stats.skipped,
        "failed": stats.failed,
    }
    if json_output:
        dump_json(payload)
        return
    typer.echo(f"indexed={stats.indexed} skipped={stats.skipped} failed={stats.failed}")
    typer.echo(f"database={stats.database}")


@app.command("search")
def search_command(
    query: str = typer.Argument(..., help="Search query."),
    root: Path = typer.Option(Path("."), "--root", help="Indexed root directory."),
    database: Path | None = typer.Option(None, "--db", help="SQLite database path."),
    limit: int = typer.Option(10, "--limit", min=1, max=100, help="Maximum hits."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    hits = search_index(query, root=root, database=database, limit=limit)
    if json_output:
        dump_json({"query": query, "hits": [asdict(hit) for hit in hits]})
        return
    for hit in hits:
        typer.echo(f"{hit.path} score={hit.score:.4f}")
        typer.echo(f"  {hit.snippet}")


@app.command("context")
def context_command(
    query: str = typer.Argument(..., help="Search query for review context."),
    root: Path = typer.Option(Path("."), "--root", help="Indexed root directory."),
    database: Path | None = typer.Option(None, "--db", help="SQLite database path."),
    limit: int = typer.Option(6, "--limit", min=1, max=30, help="Maximum context entries."),
) -> None:
    for hit in search_index(query, root=root, database=database, limit=limit):
        typer.echo(f"## {hit.path}")
        typer.echo(hit.snippet)
        typer.echo("")


@app.command("impact")
def impact_command(
    path: Path = typer.Argument(..., help="Changed file path to inspect."),
    root: Path = typer.Option(Path("."), "--root", help="Indexed root directory."),
    limit: int = typer.Option(20, "--limit", min=1, max=100, help="Maximum candidates."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    hits = impact_candidates(path, root=root, limit=limit)
    if json_output:
        dump_json({"path": str(path), "hits": [asdict(hit) for hit in hits]})
        return
    for hit in hits:
        typer.echo(f"{hit.path} score={hit.score:.4f}")
        typer.echo(f"  {hit.snippet}")
