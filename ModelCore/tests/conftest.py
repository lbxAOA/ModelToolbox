"""Shared pytest fixtures for ModelCore tests."""
import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def mock_config(tmp_path):
    """Create a mock configuration."""
    config_dir = tmp_path / ".modeltoolbox"
    config_dir.mkdir()
    return {
        "root": tmp_path,
        "state_dir": config_dir,
        "cache_dir": config_dir / "cache"
    }


@pytest.fixture
def clean_loggers():
    """Clean up loggers between tests."""
    import logging
    yield
    for name in list(logging.Logger.manager.loggerDict.keys()):
        if name.startswith("modeltoolbox"):
            logger = logging.getLogger(name)
            logger.handlers.clear()
            logger.setLevel(logging.NOTSET)
