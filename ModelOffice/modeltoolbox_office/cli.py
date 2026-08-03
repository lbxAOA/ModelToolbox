from __future__ import annotations

from pathlib import Path

import typer

from modeltoolbox_core.jsonio import dump_json

from .audit import read_audit_records
from .envs import (
    clone_env,
    create_env,
    destroy_env,
    env_to_json,
    install_packages,
    list_envs,
    list_packages,
    uninstall_packages,
)
from .executor import run_in_env
from .fileops import clean_workspace, download_file, upload_file
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


@env_app.command("info")
def env_info(
    name: str,
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Show detailed information about an environment."""
    envs = {env.name: env for env in list_envs()}
    if name not in envs:
        typer.echo(f"Environment '{name}' not found", err=True)
        raise typer.Exit(1)
    
    env = envs[name]
    payload = env_to_json(env)
    
    if json_output:
        dump_json(payload)
    else:
        typer.echo(f"Name: {payload['name']}")
        typer.echo(f"Root: {payload['root']}")
        typer.echo(f"Workspace: {payload['workspace']}")
        typer.echo(f"Ready: {payload['ready']}")
        typer.echo(f"Python: {payload.get('python_version', 'unknown')}")


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


@env_app.command("clone")
def env_clone(
    source: str,
    target: str,
    copy_workspace: bool = typer.Option(False, "--copy-workspace", help="Also copy workspace files."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    try:
        env = clone_env(source, target, copy_workspace=copy_workspace)
    except (RuntimeError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    payload = env_to_json(env)
    if json_output:
        dump_json(payload)
    else:
        typer.echo(f"cloned {source} to {target}")


@env_app.command("packages")
def env_packages(
    name: str,
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    try:
        packages = list_packages(name)
    except (RuntimeError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    payload = {"env": name, "packages": packages}
    if json_output:
        dump_json(payload)
    else:
        for pkg in packages:
            typer.echo(pkg)


@env_app.command("uninstall")
def env_uninstall(
    name: str,
    packages: list[str] = typer.Argument(..., help="Package names to uninstall."),
    timeout: float = typer.Option(300, help="Uninstall timeout in seconds."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    try:
        result = uninstall_packages(name, packages, timeout=timeout)
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


@app.command()
def upload(
    env: str,
    local: Path = typer.Argument(..., help="Local file or directory path."),
    remote: str = typer.Argument(..., help="Remote path in workspace."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Upload a file or directory to sandbox workspace."""
    try:
        payload = upload_file(env, local, remote)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    if json_output:
        dump_json(payload)
    else:
        typer.echo(f"uploaded {payload['bytes']} bytes to {payload['remote']}")


@app.command()
def download(
    env: str,
    remote: str = typer.Argument(..., help="Remote path in workspace."),
    local: Path = typer.Argument(..., help="Local file or directory path."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Download a file or directory from sandbox workspace."""
    try:
        payload = download_file(env, remote, local)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    if json_output:
        dump_json(payload)
    else:
        typer.echo(f"downloaded {payload['bytes']} bytes to {payload['local']}")


@app.command()
def clean(
    env: str,
    keep_packages: bool = typer.Option(False, "--keep-packages", help="Keep venv, only remove workspace files."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Clean the workspace directory."""
    try:
        payload = clean_workspace(env, keep_packages=keep_packages)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    if json_output:
        dump_json(payload)
    else:
        typer.echo(f"removed {payload['removed_files']} files ({payload['removed_bytes']} bytes)")


@app.command()
def audit(
    limit: int = typer.Option(20, help="Maximum number of recent records to show."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Show recent audit log records."""
    records = read_audit_records(limit=limit)
    
    if json_output:
        dump_json({"records": [
            {
                "timestamp": r.timestamp,
                "env": r.env,
                "command": r.command,
                "exit_code": r.exit_code,
                "duration_ms": r.duration_ms,
            }
            for r in records
        ]})
    else:
        for r in records:
            cmd = " ".join(r.command)
            status = "✓" if r.exit_code == 0 else "✗"
            typer.echo(f"{status} [{r.timestamp}] {r.env}: {cmd} ({r.duration_ms}ms)")
