"""阶段1 训练包装：以子进程调用 ModelTraining(unsloth) 的 CLI。

严格通过子进程边界调用 AGPL 代码，不 import。默认 --dry-run 以便安全预演。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def _training_dir() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "ModelTraining" / "cli.py").is_file():
            return parent / "ModelTraining"
    raise FileNotFoundError("未找到 ModelTraining/cli.py")


def build_train_cmd(config: Path, dry_run: bool = True) -> List[str]:
    cli = _training_dir() / "cli.py"
    cmd = [sys.executable, str(cli), "train", "--config", str(config)]
    if dry_run:
        cmd.append("--dry-run")
    return cmd


def build_export_cmd(extra: Optional[List[str]] = None) -> List[str]:
    cli = _training_dir() / "cli.py"
    return [sys.executable, str(cli), "export", *(extra or [])]


def run(cmd: List[str], execute: bool = False) -> int:
    """打印命令；execute=True 时真正运行。返回退出码(未执行则0)。"""
    print("$", " ".join(cmd))
    if not execute:
        return 0
    return subprocess.run(cmd).returncode
