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


def clone_env(
    source_name: str,
    target_name: str,
    *,
    project_root: Path | None = None,
    copy_workspace: bool = False,
) -> OfficeEnv:
    """Clone an existing environment.
    
    Args:
        source_name: Source environment name
        target_name: Target environment name
        project_root: Optional project root
        copy_workspace: If True, also copy workspace files
        
    Returns:
        New cloned environment
    """
    source = get_env(source_name, project_root=project_root)
    if not source.python.exists():
        raise ValueError(f"Source environment not ready: {source_name}")
    
    target = create_env(target_name, project_root=project_root)
    
    # Get installed packages from source
    result = run_command(
        [str(source.python), "-m", "pip", "freeze"],
        timeout=60,
    )
    
    if result.returncode == 0 and result.stdout.strip():
        packages = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
        if packages:
            install_result = run_command(
                [str(target.python), "-m", "pip", "install", *packages],
                timeout=600,
            )
            if install_result.returncode != 0:
                raise RuntimeError(f"Failed to install packages: {install_result.stderr}")
    
    # Optionally copy workspace
    if copy_workspace and source.workspace.exists():
        if target.workspace.exists():
            shutil.rmtree(target.workspace)
        shutil.copytree(source.workspace, target.workspace)
    
    return target


def list_packages(name: str, *, project_root: Path | None = None) -> list[str]:
    """List installed packages in an environment.
    
    Args:
        name: Environment name
        project_root: Optional project root
        
    Returns:
        List of package specifiers (e.g., ["numpy==1.24.0"])
    """
    env = create_env(name, project_root=project_root)
    result = run_command([str(env.python), "-m", "pip", "freeze"], timeout=60)
    
    if result.returncode != 0:
        raise RuntimeError(f"Failed to list packages: {result.stderr}")
    
    return [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]


def uninstall_packages(
    name: str,
    packages: list[str],
    *,
    project_root: Path | None = None,
    timeout: float = 300,
) -> ProcessResult:
    """Uninstall packages from an environment.
    
    Args:
        name: Environment name
        packages: Package names to uninstall
        project_root: Optional project root
        timeout: Operation timeout
        
    Returns:
        Process result
    """
    if not packages:
        raise ValueError("At least one package is required")
    
    env = create_env(name, project_root=project_root)
    return run_command(
        [str(env.python), "-m", "pip", "uninstall", "-y", *packages],
        timeout=timeout,
    )


def env_to_json(env: OfficeEnv) -> dict[str, str | bool]:
    return {
        "name": env.name,
        "root": str(env.root),
        "venv": str(env.venv),
        "workspace": str(env.workspace),
        "python": str(env.python),
        "ready": env.python.exists(),
    }