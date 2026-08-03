"""CLI commands for ModelMemory."""

from __future__ import annotations

from pathlib import Path

import typer

from modeltoolbox_core.jsonio import dump_json

from .api import CodeGraph
from .config import MemoryConfig

app = typer.Typer(help="Code knowledge graph for understanding and analyzing codebases.")


def register(root: typer.Typer) -> None:
    root.add_typer(app, name="memory")


@app.command()
def init(
    path: Path = typer.Argument(Path("."), help="Project directory to initialize."),
) -> None:
    """Initialize ModelMemory for a project."""
    config = MemoryConfig()
    config.project_root = path.resolve()
    
    try:
        graph = CodeGraph(config)
        graph.init()
        typer.echo(f"✓ Initialized ModelMemory for {path}")
        typer.echo(f"Neo4j URI: {config.neo4j.uri}")
    except ImportError as e:
        typer.echo(f"✗ Missing dependencies: {e}", err=True)
        typer.echo("Install with: pip install neo4j tree-sitter tree-sitter-python", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"✗ Failed to initialize: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def parse(
    path: Path = typer.Argument(Path("."), help="Directory to parse."),
    include: list[str] | None = typer.Option(None, "--include", help="File patterns to include."),
    exclude: list[str] | None = typer.Option(None, "--exclude", help="File patterns to exclude."),
    json_output: bool = typer.Option(False, "--json", help="Output JSON."),
) -> None:
    """Parse codebase and build the knowledge graph."""
    try:
        graph = CodeGraph.from_project(path)
        typer.echo("Parsing codebase...")
        stats = graph.parse(include=include, exclude=exclude)
        graph.close()
        
        if json_output:
            dump_json(stats)
        else:
            typer.echo(f"✓ Parsed {stats['files']} files")
            typer.echo(f"  - Nodes: {stats['nodes']}")
            typer.echo(f"  - Relationships: {stats['relationships']}")
            typer.echo(f"  - Skipped: {stats['skipped']}")
            if stats['failed'] > 0:
                typer.echo(f"  - Failed: {stats['failed']}")
    except Exception as e:
        typer.echo(f"✗ Parse failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def update(
    paths: list[Path] = typer.Argument(..., help="Files to update."),
    json_output: bool = typer.Option(False, "--json", help="Output JSON."),
) -> None:
    """Incrementally update the graph for changed files."""
    try:
        graph = CodeGraph()
        typer.echo(f"Updating {len(paths)} files...")
        stats = graph.update(paths)
        graph.close()
        
        if json_output:
            dump_json(stats)
        else:
            typer.echo(f"✓ Updated {stats['updated']} files")
            if stats['failed'] > 0:
                typer.echo(f"  - Failed: {stats['failed']}")
    except Exception as e:
        typer.echo(f"✗ Update failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query."),
    limit: int = typer.Option(10, "--limit", help="Maximum results."),
    json_output: bool = typer.Option(False, "--json", help="Output JSON."),
) -> None:
    """Search for code using full-text search."""
    try:
        graph = CodeGraph()
        results = graph.search(query, limit=limit)
        graph.close()
        
        if json_output:
            dump_json({
                "query": query,
                "results": [
                    {
                        "name": r.node.name,
                        "path": r.node.path,
                        "line": r.node.line_start,
                        "score": r.score,
                    }
                    for r in results
                ]
            })
        else:
            typer.echo(f"Found {len(results)} results for '{query}':\n")
            for r in results:
                typer.echo(f"  {r.node.name} ({r.node.path}:{r.node.line_start})")
                typer.echo(f"    Score: {r.score:.2f}")
                if r.snippet:
                    typer.echo(f"    {r.snippet[:100]}")
                typer.echo()
    except Exception as e:
        typer.echo(f"✗ Search failed: {e}", err=True)
        raise typer.Exit(1)


@app.command("search-semantic")
def search_semantic_command(
    query: str = typer.Argument(..., help="Natural language query."),
    limit: int = typer.Option(10, "--limit", help="Maximum results."),
) -> None:
    """Search for code using semantic similarity."""
    try:
        graph = CodeGraph()
        results = graph.search_semantic(query, limit=limit)
        graph.close()
        
        typer.echo(f"Found {len(results)} results for '{query}':\n")
        for r in results:
            typer.echo(f"  {r.node.name} ({r.node.path}:{r.node.line_start})")
            typer.echo(f"    Similarity: {r.score:.2f}")
            typer.echo()
    except NotImplementedError:
        typer.echo("✗ Semantic search requires embedding configuration", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"✗ Search failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def stats(
    json_output: bool = typer.Option(False, "--json", help="Output JSON."),
) -> None:
    """Show graph statistics."""
    try:
        graph = CodeGraph()
        statistics = graph.get_stats()
        graph.close()
        
        if json_output:
            dump_json(statistics)
        else:
            typer.echo("Graph Statistics:\n")
            typer.echo(f"Total Nodes: {statistics['total_nodes']}")
            for label, count in statistics['nodes'].items():
                typer.echo(f"  - {label}: {count}")
            typer.echo(f"\nTotal Relationships: {statistics['total_relationships']}")
            for rel_type, count in statistics['relationships'].items():
                typer.echo(f"  - {rel_type}: {count}")
    except Exception as e:
        typer.echo(f"✗ Failed to get stats: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def impact(
    path: str = typer.Argument(..., help="File path."),
    name: str | None = typer.Option(None, "--name", help="Function or class name."),
) -> None:
    """Analyze impact of changing code."""
    try:
        graph = CodeGraph()
        analysis = graph.analyze_impact(path, name)
        graph.close()
        
        typer.echo(f"Impact Analysis for {path}::{name or 'file'}\n")
        typer.echo(f"Direct impacts: {len(analysis.direct_impacts)}")
        typer.echo(f"Indirect impacts: {len(analysis.indirect_impacts)}")
        typer.echo(f"Total impacts: {analysis.total_impacts}")
    except NotImplementedError:
        typer.echo("✗ Impact analysis not yet implemented", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"✗ Analysis failed: {e}", err=True)
        raise typer.Exit(1)
