"""File operations for sandbox environments."""
from __future__ import annotations

import shutil
from pathlib import Path

from modeltoolbox_core.paths import resolve_in_root

from .envs import OfficeEnv, create_env


def upload_file(
    name: str,
    local_path: Path | str,
    remote_path: Path | str,
    *,
    project_root: Path | None = None,
) -> dict[str, str | int]:
    """Upload a file from local filesystem to sandbox workspace.
    
    Args:
        name: Environment name
        local_path: Local file path
        remote_path: Target path in workspace (relative)
        project_root: Optional project root
        
    Returns:
        Dictionary with upload details
    """
    env = create_env(name, project_root=project_root)
    local = Path(local_path).resolve()
    
    if not local.exists():
        raise FileNotFoundError(f"Local file not found: {local}")
    
    # Strip 'workspace/' prefix if present
    remote_str = str(remote_path).replace("\\", "/")
    if remote_str.startswith("workspace/"):
        remote_str = remote_str[10:]  # Remove 'workspace/' prefix
    
    target = resolve_in_root(env.workspace, remote_str)
    target.parent.mkdir(parents=True, exist_ok=True)
    
    if local.is_file():
        shutil.copy2(local, target)
        size = target.stat().st_size
    elif local.is_dir():
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(local, target)
        size = sum(f.stat().st_size for f in target.rglob("*") if f.is_file())
    else:
        raise ValueError(f"Path is neither file nor directory: {local}")
    
    return {
        "env": name,
        "local": str(local),
        "remote": str(target.relative_to(env.workspace)),
        "bytes": size,
    }


def download_file(
    name: str,
    remote_path: Path | str,
    local_path: Path | str,
    *,
    project_root: Path | None = None,
) -> dict[str, str | int]:
    """Download a file from sandbox workspace to local filesystem.
    
    Args:
        name: Environment name
        remote_path: Source path in workspace (relative)
        local_path: Target local file path
        project_root: Optional project root
        
    Returns:
        Dictionary with download details
    """
    env = create_env(name, project_root=project_root)
    
    # Strip 'workspace/' prefix if present
    remote_str = str(remote_path).replace("\\", "/")
    if remote_str.startswith("workspace/"):
        remote_str = remote_str[10:]  # Remove 'workspace/' prefix
    
    source = resolve_in_root(env.workspace, remote_str)
    
    if not source.exists():
        raise FileNotFoundError(f"Remote file not found: {remote_path}")
    
    target = Path(local_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    
    if source.is_file():
        shutil.copy2(source, target)
        size = target.stat().st_size
    elif source.is_dir():
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
        size = sum(f.stat().st_size for f in target.rglob("*") if f.is_file())
    else:
        raise ValueError(f"Path is neither file nor directory: {source}")
    
    return {
        "env": name,
        "remote": str(source.relative_to(env.workspace)),
        "local": str(target),
        "bytes": size,
    }


def clean_workspace(
    name: str,
    *,
    keep_packages: bool = False,
    project_root: Path | None = None,
) -> dict[str, str | int]:
    """Clean the workspace directory.
    
    Args:
        name: Environment name
        keep_packages: If True, only remove files, keep venv intact
        project_root: Optional project root
        
    Returns:
        Dictionary with cleanup details
    """
    env = create_env(name, project_root=project_root)
    
    if not env.workspace.exists():
        return {"env": name, "removed_bytes": 0, "removed_files": 0}
    
    removed_bytes = 0
    removed_files = 0
    
    for item in env.workspace.iterdir():
        if item.is_file():
            removed_bytes += item.stat().st_size
            removed_files += 1
            item.unlink()
        elif item.is_dir():
            size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
            count = sum(1 for f in item.rglob("*") if f.is_file())
            removed_bytes += size
            removed_files += count
            shutil.rmtree(item)
    
    return {
        "env": name,
        "removed_bytes": removed_bytes,
        "removed_files": removed_files,
    }
