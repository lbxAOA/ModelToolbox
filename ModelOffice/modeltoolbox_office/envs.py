from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from modeltoolbox_core.config import default_config
from modeltoolbox_core.proc import ProcessResult, run_command


@dataclass(frozen=True)
class OfficeEnv:
    name: str
    root: Path
    venv: Path
    workspace: Path

    @property
    def python(self) -> Path:
        if sys.platform == "win32":
            return self.venv / "Scripts" / "python.exe"
        return self.venv / "bin" / "python"

    @property
    def pip(self) -> Path:
        if sys.platform == "win32":
            return self.venv / "Scripts" / "pip.exe"
        return self.venv / "bin" / "pip"


def office_root(project_root: Path | None = None) -> Path:
    return default_config(project_root).state_dir / "office"


def envs_root(project_root: Path | None = None) -> Path:
    return office_root(project_root) / "envs"


def validate_env_name(name: str) -> str:
    if not name:
        raise ValueError("Environment name is required")
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    if any(ch not in allowed for ch in name) or name in {".", ".."}:
        raise ValueError("Environment name may only contain letters, numbers, dot, dash, and underscore")
    return name


def get_env(name: str, *, project_root: Path | None = None) -> OfficeEnv:
    checked = validate_env_name(name)
    root = (envs_root(project_root) / checked).resolve()
    return OfficeEnv(name=checked, root=root, venv=root / "venv", workspace=root / "workspace")


def list_envs(*, project_root: Path | None = None) -> list[OfficeEnv]:
    root = envs_root(project_root)
    if not root.exists():
        return []
    return [get_env(path.name, project_root=project_root) for path in sorted(root.iterdir()) if path.is_dir()]


def create_env(name: str, *, project_root: Path | None = None, python: Path | None = None) -> OfficeEnv:
    env = get_env(name, project_root=project_root)
    env.root.mkdir(parents=True, exist_ok=True)
    env.workspace.mkdir(parents=True, exist_ok=True)
    if not env.python.exists():
        interpreter = str((python or Path(sys.executable)).resolve())
        result = run_command([interpreter, "-m", "venv", str(env.venv)], timeout=300)
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout or "venv creation failed")
    return env


def destroy_env(name: str, *, project_root: Path | None = None) -> None:
    env = get_env(name, project_root=project_root)
    if env.root.exists():
        shutil.rmtree(env.root)


def install_packages(
    name: str,
    packages: list[str],
    *,
    project_root: Path | None = None,
    timeout: float = 600,
) -> ProcessResult:
    if not packages:
        raise ValueError("At least one package is required")
    env = create_env(name, project_root=project_root)
    return run_command([str(env.python), "-m", "pip", "install", *packages], timeout=timeout)


def env_to_json(env: OfficeEnv) -> dict[str, str | bool]:
    return {
        "name": env.name,
        "root": str(env.root),
        "venv": str(env.venv),
        "workspace": str(env.workspace),
        "python": str(env.python),
        "ready": env.python.exists(),
    }