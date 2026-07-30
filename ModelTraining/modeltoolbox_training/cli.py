from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import typer

from modeltoolbox_core.jsonio import dump_json

from .core import (
    ARCH_PRESETS,
    compute_stats,
    distill_plan,
    estimate_resources,
    generate_axolotl_config,
    generate_hf_config,
    inspect_dataset,
    recommend_architecture,
    training_plan,
    validate_dataset,
    write_export_manifest,
)

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
    validate: bool = typer.Option(False, "--validate", help="Validate dataset format and quality."),
    stats: bool = typer.Option(False, "--stats", help="Compute detailed statistics."),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as errors in validation."),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    try:
        if validate:
            result = validate_dataset(dataset, strict=strict)
            if json_output:
                dump_json(asdict(result))
                return
            typer.echo(f"status={result.status} samples={result.total_samples} duplicates={result.duplicates}")
            if result.warnings:
                typer.echo("Warnings:")
                for warning in result.warnings[:10]:  # 限制显示数量
                    typer.echo(f"  - {warning}")
            if result.errors:
                typer.echo("Errors:", err=True)
                for error in result.errors[:10]:
                    typer.echo(f"  - {error}", err=True)
            if result.status == "error":
                raise typer.Exit(1)
        elif stats:
            result = compute_stats(dataset, verbose=verbose)
            if json_output:
                payload = asdict(result)
                dump_json(payload)
                return
            typer.echo(f"samples={result.total_samples} avg_length={result.avg_length:.1f} vocab={result.vocab_size_estimate}")
            if verbose:
                typer.echo(f"Percentiles: p50={result.length_percentiles['p50']} p90={result.length_percentiles['p90']} p99={result.length_percentiles['p99']}")
        else:
            info = inspect_dataset(dataset)
            payload = asdict(info)
            payload["path"] = str(info.path)
            if json_output:
                dump_json(payload)
                return
            typer.echo(f"files={info.files} examples={info.examples} bytes={info.bytes}")
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error


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


@app.command("recommend")
def recommend_command(
    dataset: Path = typer.Argument(..., help="Dataset file or directory."),
    gpu_memory: str | None = typer.Option(None, "--gpu-memory", help="Available GPU memory (e.g., '24GB')."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    try:
        result = recommend_architecture(dataset, gpu_memory=gpu_memory)
        if json_output:
            dump_json(result)
            return
        typer.echo(f"Recommended: {result['recommended_model']} with {result['recommended_method']}")
        typer.echo(f"Reason: {result['reason']}")
        if result.get("alternatives"):
            typer.echo("\nAlternatives:")
            for alt in result["alternatives"]:
                typer.echo(f"  - {alt['model']}: {alt['reason']}")
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error


@app.command("estimate")
def estimate_command(
    dataset: Path = typer.Argument(..., help="Dataset file or directory."),
    arch: str = typer.Option("tiny-decoder", "--arch", help="Architecture preset."),
    method: str = typer.Option("lora", "--method", help="Training method: lora, qlora, full."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    try:
        result = estimate_resources(dataset, arch=arch, method=method)
        if json_output:
            dump_json(result)
            return
        typer.echo(f"GPU Memory: {result['gpu_memory']['minimum']} (min) / {result['gpu_memory']['recommended']} (recommended)")
        typer.echo(f"Training Time: {result['time_estimate']['total_hours']} hours (~{result['time_estimate']['total_minutes']} minutes)")
        typer.echo(f"Estimated Cost: ${result['cost_estimate']['total_usd']} on {result['cost_estimate']['provider']}")
        typer.echo(f"Model Params: {result['model_params_millions']}M (trainable: {result['trainable_params_millions']}M)")
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error


@app.command("generate-config")
def generate_config_command(
    plan_file: Path = typer.Argument(..., help="Training plan JSON file."),
    format: str = typer.Option("huggingface", "--format", help="Config format: huggingface, axolotl."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output config file."),
) -> None:
    try:
        import json
        plan = json.loads(plan_file.read_text(encoding="utf-8"))
        
        if format == "huggingface":
            config = generate_hf_config(plan)
        elif format == "axolotl":
            config = generate_axolotl_config(plan)
        else:
            typer.echo(f"Unknown format: {format}", err=True)
            raise typer.Exit(1)
        
        if output:
            output.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            typer.echo(f"Config written to {output}")
        else:
            dump_json(config, pretty=True)
    except Exception as error:
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
