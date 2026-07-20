"""pipeline_mt —— ModelToolbox 四阶段管线胶水层。

阶段0 数据合成(datagen) → 阶段1 视觉微调(train, 子进程调 unsloth) →
阶段2 Ollama 承载(serve) → 阶段3 双通道(见 orchestrator)。

各阶段解耦：可单独运行，也可经 CLI 串起。不 import AGPL 代码。
"""
from __future__ import annotations

from .datagen import DatagenConfig, QAPair, generate, make_provider_teacher
from .serve import ModelfileSpec, render_modelfile, write_modelfile
from .train import build_export_cmd, build_train_cmd

__all__ = [
    "DatagenConfig",
    "QAPair",
    "generate",
    "make_provider_teacher",
    "ModelfileSpec",
    "render_modelfile",
    "write_modelfile",
    "build_train_cmd",
    "build_export_cmd",
]
__version__ = "0.1.0"
