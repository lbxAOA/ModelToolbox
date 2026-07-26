from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json


ARCH_PRESETS: dict[str, dict[str, object]] = {
    "tiny-decoder": {
        "model_type": "decoder-only-transformer",
        "hidden_size": 256,
        "layers": 4,
        "heads": 4,
        "context_length": 1024,
        "features": ["rope", "swiglu"],
    },
    "small-decoder": {
        "model_type": "decoder-only-transformer",
        "hidden_size": 512,
        "layers": 8,
        "heads": 8,
        "context_length": 2048,
        "features": ["rope", "gqa", "swiglu"],
    },
}

EXPORT_FORMATS = {"safetensors", "onnx", "gguf"}


@dataclass(frozen=True)
class DatasetInfo:
    path: Path
    files: int
    bytes: int
    examples: int
    formats: dict[str, int]


def inspect_dataset(path: Path | str) -> DatasetInfo:
    dataset_path = Path(path).resolve()
    if not dataset_path.exists():
        raise ValueError(f"Dataset path does not exist: {dataset_path}")
    paths = [dataset_path] if dataset_path.is_file() else [item for item in dataset_path.rglob("*") if item.is_file()]
    files = 0
    total_bytes = 0
    examples = 0
    formats: dict[str, int] = {}
    for item in paths:
        suffix = item.suffix.lower() or "<none>"
        formats[suffix] = formats.get(suffix, 0) + 1
        try:
            total_bytes += item.stat().st_size
            if suffix in {".jsonl", ".txt", ".md", ".csv"}:
                examples += sum(1 for line in item.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())
            else:
                examples += 1
            files += 1
        except OSError:
            continue
    return DatasetInfo(path=dataset_path, files=files, bytes=total_bytes, examples=examples, formats=formats)


def training_plan(dataset: Path | str, *, arch: str = "tiny-decoder", output: Path | str | None = None) -> dict[str, object]:
    if arch not in ARCH_PRESETS:
        raise ValueError(f"Unknown architecture preset: {arch}")
    info = inspect_dataset(dataset)
    output_path = Path(output).resolve() if output else Path(".modeltoolbox/training/runs/latest").resolve()
    tokens_estimate = max(info.examples * 256, 1)
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "path": str(info.path),
            "files": info.files,
            "bytes": info.bytes,
            "examples": info.examples,
            "formats": info.formats,
        },
        "architecture": {"name": arch, **ARCH_PRESETS[arch]},
        "training": {
            "mode": "lora",
            "estimated_tokens": tokens_estimate,
            "batch_size": 1 if tokens_estimate < 10000 else 2,
            "max_steps": min(max(tokens_estimate // 512, 10), 1000),
            "output": str(output_path),
        },
    }


def distill_plan(capabilities: list[str], *, keep_weight: float = 1.0, degrade_weight: float = 0.2) -> dict[str, object]:
    if not capabilities:
        raise ValueError("At least one capability must be provided")
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "objective": "weighted-knowledge-distillation",
        "capabilities": [
            {"name": capability, "teacher_weight": keep_weight, "degrade_weight": degrade_weight}
            for capability in capabilities
        ],
        "loss": "sum(capability_weight * kd_loss) + supervised_loss",
    }


def write_export_manifest(run_dir: Path | str, *, export_format: str, output: Path | str | None = None) -> Path:
    if export_format not in EXPORT_FORMATS:
        raise ValueError(f"Unsupported export format: {export_format}")
    run_path = Path(run_dir).resolve()
    output_path = Path(output).resolve() if output else run_path / f"export-{export_format}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_path),
        "format": export_format,
        "status": "planned",
        "notes": "This manifest records the export request. Format-specific converters are plugged in after training artifacts exist.",
    }
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path
