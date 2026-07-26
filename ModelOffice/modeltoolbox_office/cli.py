from __future__ import annotations

from pathlib import Path

import typer

from modeltoolbox_core.jsonio import dump_json

from .envs import create_env, destroy_env, env_to_json, install_packages, list_envs
from .executor import run_in_env
from .snapshot import create_snapshot, list_snapshots, restore_snapshot

app = typer.Typer(help="Manage local sandbox environments for model-assisted coding.")
env_app = typer.Typer(help="Manage local Python sandbox environments.", no_args_is_help=True)
snapshot_app = typer.Typer(help="Create and restore workspace snapshots.", no_args_is_help=True)
app.add_typer(env_app, name="env")
app.add_typer(snapshot_app, name="snapshot")


def register(root: typer.Typer) -> None:
    root.add_typer(app, name="office")


@app.command()
def doctor() -> None:
    typer.echo("office: registered")


@env_app.command("list")
def env_list(json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON.")) -> None:
    payload = {"envs": [env_to_json(env) for env in list_envs()]}
    if json_output:
        dump_json(payload)
        return
    for env in payload["envs"]:
        typer.echo(f"{env['name']} ready={env['ready']} workspace={env['workspace']}")


@env_app.command("create")
def env_create(
    name: str,
    python: Path | None = typer.Option(None, help="Python interpreter to seed the venv."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    try:
        env = create_env(name, python=python)
    except (RuntimeError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    payload = env_to_json(env)
    if json_output:
        dump_json(payload)
    else:
        typer.echo(f"created {payload['name']} at {payload['root']}")


@env_app.command("install")
def env_install(
    name: str,
    packages: list[str] = typer.Argument(..., help="Package names or requirement specifiers."),
    timeout: float = typer.Option(600, help="Install timeout in seconds."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    try:
        result = install_packages(name, packages, timeout=timeout)
    except (RuntimeError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    payload = {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    if json_output:
        dump_json(payload)
    else:
        typer.echo(result.stdout, nl=False)
        typer.echo(result.stderr, err=True, nl=False)
    if result.returncode != 0:
        raise typer.Exit(result.returncode)


@env_app.command("destroy")
def env_destroy(name: str) -> None:
    try:
        destroy_env(name)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"destroyed {name}")


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def exec(
    ctx: typer.Context,
    name: str,
    cwd: Path | None = typer.Option(None, help="Working directory relative to the env workspace."),
    timeout: float = typer.Option(120, help="Execution timeout in seconds."),
    network: bool = typer.Option(True, help="Expose normal network-related environment settings."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    args = list(ctx.args)
    try:
        result = run_in_env(name, args, cwd=cwd, timeout=timeout, network=network)
    except (RuntimeError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    payload = {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    if json_output:
        dump_json(payload)
    else:
        typer.echo(result.stdout, nl=False)
        typer.echo(result.stderr, err=True, nl=False)
    if result.returncode != 0:
        raise typer.Exit(result.returncode)


@snapshot_app.command("list")
def snapshot_list(
    env: str,
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    payload = {"env": env, "snapshots": list_snapshots(env)}
    if json_output:
        dump_json(payload)
    else:
        for item in payload["snapshots"]:
            typer.echo(item)


@snapshot_app.command("create")
def snapshot_create(
    env: str,
    name: str,
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    try:
        payload = create_snapshot(env, name)
    except (FileExistsError, RuntimeError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    if json_output:
        dump_json(payload)
    else:
        typer.echo(f"snapshot {name} captured for {env}")


@snapshot_app.command("restore")
def snapshot_restore(
    env: str,
    name: str,
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    try:
        payload = restore_snapshot(env, name)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    if json_output:
        dump_json(payload)
    else:
        typer.echo(f"snapshot {name} restored into {env}")
