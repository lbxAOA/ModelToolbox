from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import typer

from modeltoolbox_core.jsonio import dump_json

from .core import ARCH_PRESETS, distill_plan, inspect_dataset, training_plan, write_export_manifest

app = typer.Typer(help="Train, distill, evaluate, and export small model architectures.")


def register(root: typer.Typer) -> None:
    root.add_typer(app, name="train")


@app.command()
def doctor() -> None:
    typer.echo(f"train: registered arch_presets={len(ARCH_PRESETS)}")


@app.command("arch")
def arch_command(
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    if json_output:
        dump_json({"presets": ARCH_PRESETS})
        return
    for name, preset in ARCH_PRESETS.items():
        typer.echo(f"{name}\t{preset['model_type']} layers={preset['layers']} hidden={preset['hidden_size']}")


@app.command("data")
def data_command(
    dataset: Path = typer.Argument(..., help="Dataset file or directory."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    try:
        info = inspect_dataset(dataset)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error
    payload = asdict(info)
    payload["path"] = str(info.path)
    if json_output:
        dump_json(payload)
        return
    typer.echo(f"files={info.files} examples={info.examples} bytes={info.bytes}")


@app.command("plan")
def plan_command(
    dataset: Path = typer.Argument(..., help="Dataset file or directory."),
    arch: str = typer.Option("tiny-decoder", "--arch", help="Architecture preset."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Training output directory."),
) -> None:
    try:
        dump_json(training_plan(dataset, arch=arch, output=output), pretty=True)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error


@app.command("distill-plan")
def distill_plan_command(
    capability: list[str] = typer.Argument(..., help="Capability names to preserve."),
    keep_weight: float = typer.Option(1.0, "--keep-weight", min=0.0, help="Teacher loss weight for preserved capabilities."),
    degrade_weight: float = typer.Option(0.2, "--degrade-weight", min=0.0, help="Teacher loss weight for degraded capabilities."),
) -> None:
    try:
        dump_json(distill_plan(capability, keep_weight=keep_weight, degrade_weight=degrade_weight), pretty=True)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error


@app.command("export")
def export_command(
    run_dir: Path = typer.Argument(..., help="Training run directory."),
    export_format: str = typer.Option("safetensors", "--format", help="Export format: safetensors, onnx, gguf."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Manifest output path."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    try:
        path = write_export_manifest(run_dir, export_format=export_format, output=output)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error
    if json_output:
        dump_json({"manifest": str(path)})
        return
    typer.echo(path)
