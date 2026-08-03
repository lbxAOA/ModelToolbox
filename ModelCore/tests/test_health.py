"""Tests for modeltoolbox_core.health module."""
import pytest
import sys
from modeltoolbox_core.health import check_dependency, get_version_info, health_check


def test_check_dependency_python():
    """Test checking Python dependency."""
    available, version = check_dependency("python", "python --version")
    assert available is True
    assert version is not None
    assert "Python" in version or "python" in version.lower()


def test_check_dependency_nonexistent():
    """Test checking non-existent dependency."""
    available, version = check_dependency("nonexistent_command_xyz")
    assert available is False
    assert version is None


def test_get_version_info():
    """Test getting version information."""
    info = get_version_info()
    
    assert "python" in info
    assert "platform" in info
    assert info["platform"] == sys.platform
    
    python_version = info["python"]
    assert "." in python_version
    parts = python_version.split(".")
    assert len(parts) >= 2


def test_health_check():
    """Test complete health check."""
    result = health_check()
    
    assert "status" in result
    assert result["status"] == "healthy"
    assert "version_info" in result
    assert "dependencies" in result
    
    deps = result["dependencies"]
    assert isinstance(deps, dict)
    
    for dep_name, dep_info in deps.items():
        assert "available" in dep_info
        assert "version" in dep_info
        assert isinstance(dep_info["available"], bool)


def test_check_dependency_timeout():
    """Test dependency check with timeout."""
    available, version = check_dependency("sleep", "sleep 10")
    assert available is False
