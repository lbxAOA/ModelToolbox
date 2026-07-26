from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import typer

from modeltoolbox_core.jsonio import dump_json
from modeltoolbox_provider.providers import (
    ProviderConfig,
    create_provider,
    provider_names,
)
from modeltoolbox_provider.runtimes import available_runtimes, run_runtime
from modeltoolbox_provider.types import ChatMessage, ProviderError

app = typer.Typer(help="Route model APIs and local agent runtimes.")
runtime_app = typer.Typer(
    help="Run external coding-agent CLIs through the shared process layer."
)


def register(root: typer.Typer) -> None:
    root.add_typer(app, name="provider")


@app.command("doctor")
def doctor() -> None:
    typer.echo("provider: registered")


@app.command("list")
def list_providers(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit structured JSON.",
    ),
) -> None:
    names = provider_names()
    if json_output:
        dump_json({"providers": list(names)})
        return
    for name in names:
        typer.echo(name)


@app.command("models")
def models(
    provider: str = typer.Option("ollama", "--provider", "-p"),
    base_url: str | None = typer.Option(None, "--base-url"),
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        envvar="MTB_PROVIDER_API_KEY",
    ),
    timeout: float = typer.Option(30.0, "--timeout"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    try:
        selected = create_provider(
            ProviderConfig(
                name=provider,
                base_url=base_url,
                api_key=api_key,
                timeout=timeout,
            )
        )
        rows = [asdict(model) for model in selected.models()]
    except (ProviderError, ValueError) as exc:
        typer.echo(f"provider error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    if json_output:
        dump_json({"models": rows})
        return
    for row in rows:
        typer.echo(row["name"])


@app.command("capabilities")
def capabilities(
    provider: str = typer.Option("ollama", "--provider", "-p"),
    base_url: str | None = typer.Option(None, "--base-url"),
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        envvar="MTB_PROVIDER_API_KEY",
    ),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    try:
        selected = create_provider(
            ProviderConfig(
                name=provider,
                base_url=base_url,
                api_key=api_key,
            )
        )
        row = asdict(selected.capabilities())
    except ValueError as exc:
        typer.echo(f"provider error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    if json_output:
        dump_json(row)
        return
    for key, value in row.items():
        typer.echo(f"{key}: {value}")


@app.command("chat")
def chat(
    prompt: str = typer.Argument(...),
    provider: str = typer.Option("ollama", "--provider", "-p"),
    model: str | None = typer.Option(None, "--model", "-m"),
    base_url: str | None = typer.Option(None, "--base-url"),
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        envvar="MTB_PROVIDER_API_KEY",
    ),
    timeout: float = typer.Option(60.0, "--timeout"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    try:
        selected = create_provider(
            ProviderConfig(
                name=provider,
                base_url=base_url,
                api_key=api_key,
                model=model,
                timeout=timeout,
            )
        )
        result = selected.chat(
            [ChatMessage(role="user", content=prompt)],
            model=model,
        )
    except (ProviderError, ValueError) as exc:
        typer.echo(f"provider error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    if json_output:
        dump_json(asdict(result))
        return
    typer.echo(result.content)


@app.command("embed")
def embed(
    text: list[str] = typer.Argument(...),
    provider: str = typer.Option("ollama", "--provider", "-p"),
    model: str | None = typer.Option(None, "--model", "-m"),
    base_url: str | None = typer.Option(None, "--base-url"),
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        envvar="MTB_PROVIDER_API_KEY",
    ),
    timeout: float = typer.Option(60.0, "--timeout"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    try:
        selected = create_provider(
            ProviderConfig(
                name=provider,
                base_url=base_url,
                api_key=api_key,
                model=model,
                timeout=timeout,
            )
        )
        rows = [asdict(result) for result in selected.embed(text, model=model)]
    except (ProviderError, ValueError) as exc:
        typer.echo(f"provider error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    if json_output:
        dump_json({"embeddings": rows})
        return
    for row in rows:
        typer.echo(f"{row['model']}\t{len(row['embedding'])}")


@runtime_app.command("list")
def list_runtimes(
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    rows = [asdict(runtime) for runtime in available_runtimes()]
    if json_output:
        dump_json({"runtimes": rows})
        return
    for row in rows:
        marker = "ok" if row["available"] else "missing"
        typer.echo(
            f"{row['name']}\t{marker}\t"
            f"{row['path'] or row['executable']}"
        )


@runtime_app.command(
    "run",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def run(
    ctx: typer.Context,
    name: str = typer.Argument(...),
    cwd: Path | None = typer.Option(None, "--cwd"),
    timeout: float = typer.Option(300.0, "--timeout"),
) -> None:
    try:
        result = run_runtime(
            name,
            list(ctx.args),
            cwd=cwd,
            timeout=timeout,
        )
    except (ValueError, FileNotFoundError) as exc:
        typer.echo(f"runtime error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    if result.stdout:
        typer.echo(result.stdout, nl=False)
    if result.stderr:
        typer.echo(result.stderr, err=True, nl=False)
    if result.returncode:
        raise typer.Exit(code=result.returncode)


app.add_typer(runtime_app, name="runtime")
