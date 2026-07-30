"""ModelToolbox office sandbox package."""
from __future__ import annotations

from pathlib import Path

from .audit import read_audit_records, write_audit_record
from .envs import (
    OfficeEnv,
    clone_env,
    create_env,
    destroy_env,
    get_env,
    install_packages,
    list_envs,
    list_packages,
    uninstall_packages,
)
from .executor import run_in_env
from .fileops import clean_workspace, download_file, upload_file
from .snapshot import create_snapshot, list_snapshots, restore_snapshot


class Sandbox:
    """High-level Python API for sandbox management."""
    
    def __init__(self, name: str, *, project_root: Path | None = None):
        """Initialize a sandbox instance.
        
        Args:
            name: Environment name
            project_root: Optional project root directory
        """
        self.name = name
        self.project_root = project_root
        self._env: OfficeEnv | None = None
    
    @property
    def env(self) -> OfficeEnv:
        """Get or create the environment."""
        if self._env is None:
            self._env = create_env(self.name, project_root=self.project_root)
        return self._env
    
    @classmethod
    def create(
        cls,
        name: str,
        *,
        project_root: Path | None = None,
        python: Path | None = None,
    ) -> Sandbox:
        """Create a new sandbox environment.
        
        Args:
            name: Environment name
            project_root: Optional project root
            python: Python interpreter path
            
        Returns:
            New Sandbox instance
        """
        create_env(name, project_root=project_root, python=python)
        return cls(name, project_root=project_root)
    
    @classmethod
    def clone(
        cls,
        source: str,
        target: str,
        *,
        project_root: Path | None = None,
        copy_workspace: bool = False,
    ) -> Sandbox:
        """Clone an existing sandbox environment.
        
        Args:
            source: Source environment name
            target: Target environment name
            project_root: Optional project root
            copy_workspace: Copy workspace files
            
        Returns:
            New Sandbox instance for the cloned environment
        """
        clone_env(
            source,
            target,
            project_root=project_root,
            copy_workspace=copy_workspace,
        )
        return cls(target, project_root=project_root)
    
    def install(self, packages: list[str], *, timeout: float = 600) -> None:
        """Install packages in the sandbox.
        
        Args:
            packages: Package names or specifiers
            timeout: Installation timeout
        """
        result = install_packages(
            self.name,
            packages,
            project_root=self.project_root,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Installation failed: {result.stderr}")
    
    def execute(
        self,
        command: str | list[str],
        *,
        timeout: float = 120,
        network: bool = True,
        cwd: Path | str | None = None,
    ) -> dict[str, str | int]:
        """Execute a command in the sandbox.
        
        Args:
            command: Command string or list of arguments
            timeout: Execution timeout
            network: Allow network access
            cwd: Working directory
            
        Returns:
            Dictionary with stdout, stderr, and exit code
        """
        if isinstance(command, str):
            args = command.split()
        else:
            args = list(command)
        
        result = run_in_env(
            self.name,
            args,
            project_root=self.project_root,
            cwd=cwd,
            timeout=timeout,
            network=network,
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }
    
    def upload(self, local_path: Path | str, remote_path: Path | str) -> int:
        """Upload a file to the sandbox workspace.
        
        Args:
            local_path: Local file path
            remote_path: Target path in workspace
            
        Returns:
            Number of bytes uploaded
        """
        result = upload_file(
            self.name,
            local_path,
            remote_path,
            project_root=self.project_root,
        )
        return result["bytes"]
    
    def download(self, remote_path: Path | str, local_path: Path | str) -> int:
        """Download a file from the sandbox workspace.
        
        Args:
            remote_path: Source path in workspace
            local_path: Target local path
            
        Returns:
            Number of bytes downloaded
        """
        result = download_file(
            self.name,
            remote_path,
            local_path,
            project_root=self.project_root,
        )
        return result["bytes"]
    
    def clean(self, *, keep_packages: bool = False) -> dict[str, int]:
        """Clean the workspace.
        
        Args:
            keep_packages: Keep venv, only remove workspace files
            
        Returns:
            Dictionary with removed_files and removed_bytes
        """
        return clean_workspace(
            self.name,
            keep_packages=keep_packages,
            project_root=self.project_root,
        )
    
    def snapshot(self, snapshot_name: str) -> None:
        """Create a workspace snapshot.
        
        Args:
            snapshot_name: Name for the snapshot
        """
        create_snapshot(self.name, snapshot_name, project_root=self.project_root)
    
    def restore(self, snapshot_name: str) -> None:
        """Restore a workspace snapshot.
        
        Args:
            snapshot_name: Name of the snapshot to restore
        """
        restore_snapshot(self.name, snapshot_name, project_root=self.project_root)
    
    def destroy(self) -> None:
        """Destroy the sandbox environment."""
        destroy_env(self.name, project_root=self.project_root)
        self._env = None


__all__ = [
    "Sandbox",
    "OfficeEnv",
    "create_env",
    "destroy_env",
    "get_env",
    "list_envs",
    "clone_env",
    "install_packages",
    "uninstall_packages",
    "list_packages",
    "run_in_env",
    "upload_file",
    "download_file",
    "clean_workspace",
    "create_snapshot",
    "restore_snapshot",
    "list_snapshots",
    "read_audit_records",
    "write_audit_record",
]
