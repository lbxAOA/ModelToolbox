from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any


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
    "llama2-7b": {
        "model_type": "decoder-only-transformer",
        "base_model": "meta-llama/Llama-2-7b-hf",
        "hidden_size": 4096,
        "layers": 32,
        "heads": 32,
        "context_length": 4096,
        "features": ["rope", "gqa", "swiglu"],
    },
    "mistral-7b": {
        "model_type": "decoder-only-transformer",
        "base_model": "mistralai/Mistral-7B-v0.1",
        "hidden_size": 4096,
        "layers": 32,
        "heads": 32,
        "context_length": 8192,
        "features": ["rope", "gqa", "swiglu", "sliding-window"],
    },
}

EXPORT_FORMATS = {"safetensors", "onnx", "gguf"}
TRAINING_METHODS = {"lora", "qlora", "full", "prompt-tuning"}


@dataclass(frozen=True)
class DatasetInfo:
    path: Path
    files: int
    bytes: int
    examples: int
    formats: dict[str, int]


@dataclass(frozen=True)
class DatasetValidation:
    status: str  # "valid" | "warning" | "error"
    total_samples: int
    avg_length: float
    max_length: int
    min_length: int
    duplicates: int
    empty_fields: int
    warnings: list[str]
    errors: list[str]


@dataclass(frozen=True)
class DatasetStats:
    total_samples: int
    avg_length: float
    max_length: int
    min_length: int
    length_percentiles: dict[str, int]  # p25, p50, p75, p90, p99
    vocab_size_estimate: int
    duplicates: int


def validate_dataset(path: Path | str, *, strict: bool = False) -> DatasetValidation:
    """验证数据集格式和质量"""
    dataset_path = Path(path).resolve()
    if not dataset_path.exists():
        return DatasetValidation(
            status="error",
            total_samples=0,
            avg_length=0.0,
            max_length=0,
            min_length=0,
            duplicates=0,
            empty_fields=0,
            warnings=[],
            errors=[f"Dataset path does not exist: {dataset_path}"],
        )
    
    warnings: list[str] = []
    errors: list[str] = []
    samples: list[dict[str, Any]] = []
    
    try:
        if dataset_path.suffix.lower() == ".jsonl":
            content = dataset_path.read_text(encoding="utf-8")
            for line_num, line in enumerate(content.splitlines(), 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if not isinstance(obj, dict):
                        errors.append(f"Line {line_num}: Expected JSON object, got {type(obj).__name__}")
                        continue
                    samples.append(obj)
                except json.JSONDecodeError as e:
                    errors.append(f"Line {line_num}: Invalid JSON - {e}")
        elif dataset_path.suffix.lower() == ".json":
            data = json.loads(dataset_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                samples = [item for item in data if isinstance(item, dict)]
            elif isinstance(data, dict):
                samples = [data]
        else:
            warnings.append(f"Unsupported format: {dataset_path.suffix}")
    except Exception as e:
        errors.append(f"Failed to read dataset: {e}")
    
    lengths: list[int] = []
    empty_fields = 0
    seen_hashes: set[str] = set()
    duplicates = 0
    
    for sample in samples:
        if any(not v for v in sample.values()):
            empty_fields += 1
        
        text = " ".join(str(v) for v in sample.values())
        length = len(text.split())
        lengths.append(length)
        
        sample_hash = json.dumps(sample, sort_keys=True)
        if sample_hash in seen_hashes:
            duplicates += 1
        seen_hashes.add(sample_hash)
        
        if length > 2048:
            warnings.append(f"Sample exceeds 2048 tokens: {length}")
        elif length < 5:
            warnings.append(f"Very short sample: {length} tokens")
    
    total_samples = len(samples)
    avg_length = sum(lengths) / total_samples if total_samples > 0 else 0.0
    max_length = max(lengths) if lengths else 0
    min_length = min(lengths) if lengths else 0
    
    if duplicates > 0:
        warnings.append(f"{duplicates} duplicate samples found")
    
    if empty_fields > 0:
        warnings.append(f"{empty_fields} samples have empty fields")
    
    status = "error" if errors else ("warning" if warnings else "valid")
    if strict and warnings:
        status = "error"
    
    return DatasetValidation(
        status=status,
        total_samples=total_samples,
        avg_length=avg_length,
        max_length=max_length,
        min_length=min_length,
        duplicates=duplicates,
        empty_fields=empty_fields,
        warnings=warnings,
        errors=errors,
    )


def compute_stats(path: Path | str, *, verbose: bool = False) -> DatasetStats:
    """计算数据集统计信息"""
    dataset_path = Path(path).resolve()
    if not dataset_path.exists():
        raise ValueError(f"Dataset path does not exist: {dataset_path}")
    
    samples: list[dict[str, Any]] = []
    
    if dataset_path.suffix.lower() == ".jsonl":
        content = dataset_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    samples.append(obj)
            except json.JSONDecodeError:
                continue
    elif dataset_path.suffix.lower() == ".json":
        data = json.loads(dataset_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            samples = [item for item in data if isinstance(item, dict)]
        elif isinstance(data, dict):
            samples = [data]
    
    lengths: list[int] = []
    vocab: set[str] = set()
    seen_hashes: set[str] = set()
    duplicates = 0
    
    for sample in samples:
        text = " ".join(str(v) for v in sample.values())
        words = text.split()
        lengths.append(len(words))
        vocab.update(words)
        
        sample_hash = json.dumps(sample, sort_keys=True)
        if sample_hash in seen_hashes:
            duplicates += 1
        seen_hashes.add(sample_hash)
    
    total_samples = len(samples)
    avg_length = sum(lengths) / total_samples if total_samples > 0 else 0.0
    max_length = max(lengths) if lengths else 0
    min_length = min(lengths) if lengths else 0
    
    sorted_lengths = sorted(lengths)
    percentiles = {
        "p25": sorted_lengths[int(len(sorted_lengths) * 0.25)] if sorted_lengths else 0,
        "p50": sorted_lengths[int(len(sorted_lengths) * 0.50)] if sorted_lengths else 0,
        "p75": sorted_lengths[int(len(sorted_lengths) * 0.75)] if sorted_lengths else 0,
        "p90": sorted_lengths[int(len(sorted_lengths) * 0.90)] if sorted_lengths else 0,
        "p99": sorted_lengths[int(len(sorted_lengths) * 0.99)] if sorted_lengths else 0,
    }
    
    return DatasetStats(
        total_samples=total_samples,
        avg_length=avg_length,
        max_length=max_length,
        min_length=min_length,
        length_percentiles=percentiles,
        vocab_size_estimate=len(vocab),
        duplicates=duplicates,
    )


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


def recommend_architecture(dataset: Path | str, *, gpu_memory: str | None = None) -> dict[str, Any]:
    """根据数据集推荐模型架构"""
    info = inspect_dataset(dataset)
    total_samples = info.examples
    
    # 根据数据集大小推荐
    if total_samples < 1000:
        recommended_model = "tiny-decoder"
        recommended_method = "lora"
        reason = f"Small dataset ({total_samples} samples) - use tiny model with LoRA (r=8)"
    elif total_samples < 10000:
        recommended_model = "small-decoder"
        recommended_method = "lora"
        reason = f"Medium dataset ({total_samples} samples) - use small model with LoRA (r=16)"
    elif total_samples < 100000:
        recommended_model = "llama2-7b"
        recommended_method = "qlora"
        reason = f"Large dataset ({total_samples} samples) - use 7B model with QLoRA"
    else:
        recommended_model = "llama2-7b"
        recommended_method = "full"
        reason = f"Very large dataset ({total_samples} samples) - consider full fine-tuning"
    
    # GPU内存约束
    gpu_constraint = ""
    if gpu_memory:
        memory_gb = int(gpu_memory.replace("GB", "").replace("gb", "").strip())
        if memory_gb < 16 and recommended_model in ("llama2-7b", "mistral-7b"):
            recommended_method = "qlora"
            gpu_constraint = f" (adjusted for {gpu_memory} GPU memory)"
    
    return {
        "recommended_model": recommended_model,
        "recommended_method": recommended_method,
        "reason": reason + gpu_constraint,
        "dataset_info": {
            "total_samples": total_samples,
            "total_bytes": info.bytes,
        },
        "alternatives": [
            {
                "model": "mistral-7b",
                "reason": "Better for chat and instruction following",
            }
        ] if total_samples > 5000 else [],
    }


def estimate_resources(dataset: Path | str, *, arch: str = "tiny-decoder", method: str = "lora") -> dict[str, Any]:
    """预估训练资源需求"""
    info = inspect_dataset(dataset)
    
    if arch not in ARCH_PRESETS:
        raise ValueError(f"Unknown architecture: {arch}")
    
    preset = ARCH_PRESETS[arch]
    
    # 模型参数估算 (简化)
    hidden_size = int(preset.get("hidden_size", 512))
    num_layers = int(preset.get("layers", 8))
    model_params_millions = (hidden_size * hidden_size * num_layers * 12) / 1_000_000
    
    # GPU内存估算
    if method == "lora":
        trainable_ratio = 0.01  # LoRA只训练1%参数
        gpu_memory_gb = (model_params_millions * trainable_ratio * 4 * 4) / 1000  # FP32 + 梯度 + 优化器
        minimum_memory = "8GB"
        recommended_memory = "16GB"
    elif method == "qlora":
        trainable_ratio = 0.01
        gpu_memory_gb = (model_params_millions * trainable_ratio * 2 * 4) / 1000  # INT8 + 梯度
        minimum_memory = "8GB"
        recommended_memory = "16GB"
    else:  # full
        gpu_memory_gb = (model_params_millions * 4 * 4) / 1000
        minimum_memory = f"{int(gpu_memory_gb)}GB"
        recommended_memory = f"{int(gpu_memory_gb * 1.5)}GB"
    
    # 训练时间估算 (样本/分钟)
    samples_per_minute = 100  # 粗略估算
    epochs = 3
    total_minutes = (info.examples * epochs) / samples_per_minute
    
    # 成本估算 (AWS p3.2xlarge: $3.06/hour)
    cost_per_hour = 3.06
    total_hours = total_minutes / 60
    total_cost = total_hours * cost_per_hour
    
    return {
        "gpu_memory": {
            "minimum": minimum_memory,
            "recommended": recommended_memory,
            "estimated_usage": f"{gpu_memory_gb:.1f}GB",
        },
        "time_estimate": {
            "total_minutes": int(total_minutes),
            "total_hours": round(total_hours, 2),
            "per_epoch": int(total_minutes / epochs),
        },
        "cost_estimate": {
            "total_usd": round(total_cost, 2),
            "per_hour": cost_per_hour,
            "provider": "AWS p3.2xlarge (V100)",
        },
        "model_params_millions": round(model_params_millions, 2),
        "trainable_params_millions": round(model_params_millions * (0.01 if method in ("lora", "qlora") else 1.0), 2),
    }


def generate_hf_config(plan: dict[str, Any]) -> dict[str, Any]:
    """生成Hugging Face Transformers配置"""
    arch = plan.get("architecture", {})
    training = plan.get("training", {})
    
    return {
        "output_dir": training.get("output", "./outputs"),
        "num_train_epochs": 3,
        "per_device_train_batch_size": training.get("batch_size", 4),
        "learning_rate": 2e-4,
        "warmup_steps": 100,
        "logging_steps": 10,
        "save_steps": 500,
        "fp16": True,
        "gradient_checkpointing": True,
        "model_name_or_path": arch.get("base_model", "gpt2"),
    }


def generate_axolotl_config(plan: dict[str, Any]) -> dict[str, Any]:
    """生成Axolotl配置"""
    arch = plan.get("architecture", {})
    dataset = plan.get("dataset", {})
    training = plan.get("training", {})
    
    return {
        "base_model": arch.get("base_model", "meta-llama/Llama-2-7b-hf"),
        "model_type": "LlamaForCausalLM",
        "tokenizer_type": "LlamaTokenizer",
        "load_in_8bit": False,
        "load_in_4bit": True,
        "adapter": "lora",
        "lora_r": 16,
        "lora_alpha": 32,
        "lora_target_modules": ["q_proj", "v_proj"],
        "datasets": [
            {
                "path": dataset.get("path"),
                "type": "alpaca",
            }
        ],
        "num_epochs": 3,
        "learning_rate": 0.0002,
        "micro_batch_size": training.get("batch_size", 4),
        "gradient_accumulation_steps": 4,
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
