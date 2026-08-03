"""Health check utilities for ModelToolbox.

Provides dependency checking and version information reporting.
"""
import sys
import subprocess
from typing import Dict, Optional, Tuple
from pathlib import Path
from .logging import get_logger

logger = get_logger(__name__)


def check_dependency(name: str, command: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """Check if a dependency is available.
    
    Args:
        name: Dependency name (e.g., "git", "python")
        command: Optional command to test (defaults to "{name} --version")
    
    Returns:
        Tuple of (available, version_string)
    """
    if command is None:
        command = f"{name} --version"
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip().split("\n")[0]
            return True, version
        return False, None
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.debug(f"Dependency check failed for {name}: {e}")
        return False, None


def get_version_info() -> Dict[str, str]:
    """Get version information for the current environment.
    
    Returns:
        Dictionary with version information
    """
    info = {
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
    }
    
    git_available, git_version = check_dependency("git")
    if git_available:
        info["git"] = git_version or "unknown"
    
    return info


def health_check() -> Dict[str, any]:
    """Run a complete health check.
    
    Returns:
        Dictionary with health status and dependencies
    """
    version_info = get_version_info()
    
    dependencies = {}
    for dep in ["git", "node", "npm"]:
        available, version = check_dependency(dep)
        dependencies[dep] = {
            "available": available,
            "version": version
        }
    
    return {
        "status": "healthy",
        "version_info": version_info,
        "dependencies": dependencies
    }
