from __future__ import annotations

from pathlib import Path

import typer

from modeltoolbox_core.jsonio import dump_json

from .library import build_from_markdown_library, build_registry, discover_skills, search_skills

app = typer.Typer(help="Build and manage skills from ingested Markdown libraries.")


def register(root: typer.Typer) -> None:
    root.add_typer(app, name="skill")


@app.command()
def doctor() -> None:
    typer.echo(f"skill: registered skills={len(discover_skills())}")


@app.command("list")
def list_command(
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    records = discover_skills()
    if json_output:
        dump_json({"skills": [record.__dict__ for record in records]})
        return
    for record in records:
        typer.echo(f"{record.name}\t{record.path}")


@app.command("search")
def search_command(
    query: str = typer.Argument(..., help="Skill search query."),
    limit: int = typer.Option(5, "--limit", min=1, max=50, help="Maximum skills to return."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    records = search_skills(query, limit=limit)
    if json_output:
        dump_json({"query": query, "skills": [record.__dict__ for record in records]})
        return
    for record in records:
        typer.echo(f"{record.name}\t{record.description}")


@app.command("build-registry")
def build_registry_command(
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    payload = build_registry()
    if json_output:
        dump_json(payload)
        return
    typer.echo(f"skills={payload['skill_count']}")


@app.command("build-from")
def build_from_command(
    source: Path = typer.Argument(..., help="Ingested Markdown library directory."),
    name: str | None = typer.Option(None, "--name", help="Skill name. Defaults to source directory name."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Replace an existing skill."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    try:
        path = build_from_markdown_library(source, name=name, overwrite=overwrite)
    except (FileExistsError, ValueError) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error
    if json_output:
        dump_json({"skill": str(path)})
        return
    typer.echo(path)
