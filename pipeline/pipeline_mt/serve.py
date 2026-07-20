"""阶段2 承载：由导出的 GGUF(+mmproj) 生成 Ollama Modelfile 并 create。

不 import ModelTraining；只处理 GGUF 文件与 Ollama CLI。
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_DEFAULT_SYSTEM = (
    "你是一个私有领域助手，已在用户的知识库上微调，"
    "擅长该领域的概念、原理与看图判断。请准确、简洁地作答。"
)


@dataclass
class ModelfileSpec:
    gguf_path: Path
    name: str = "modeltoolbox-private"
    mmproj_path: Optional[Path] = None  # Gemma 视觉投影，缺失则纯文本
    system: str = _DEFAULT_SYSTEM
    temperature: float = 0.3
    num_ctx: int = 4096
    stop: tuple = ("<end_of_turn>",)


def render_modelfile(spec: ModelfileSpec) -> str:
    lines = [f"FROM {spec.gguf_path.as_posix()}"]
    if spec.mmproj_path:
        # Ollama 用 ADAPTER/PROJECTOR? 视觉投影经 FROM 附加行声明
        lines.append(f"# vision projector")
        lines.append(f"FROM {spec.mmproj_path.as_posix()}")
    lines.append("")
    lines.append(f'PARAMETER temperature {spec.temperature}')
    lines.append(f'PARAMETER num_ctx {spec.num_ctx}')
    for s in spec.stop:
        lines.append(f'PARAMETER stop "{s}"')
    lines.append("")
    esc = spec.system.replace('"""', '\\"\\"\\"')
    lines.append(f'SYSTEM """{esc}"""')
    lines.append("")
    return "\n".join(lines)


def write_modelfile(spec: ModelfileSpec, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_modelfile(spec), encoding="utf-8")
    return out_path


def ollama_create(name: str, modelfile: Path, run: bool = True) -> list:
    """返回 `ollama create` 命令；run=True 时执行。"""
    cmd = ["ollama", "create", name, "-f", str(modelfile)]
    if run:
        subprocess.run(cmd, check=True)
    return cmd
