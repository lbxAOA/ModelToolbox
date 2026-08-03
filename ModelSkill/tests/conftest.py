"""Shared pytest fixtures for ModelSkill tests."""
import pytest
from pathlib import Path


@pytest.fixture
def tmp_skill_library(tmp_path):
    """Create a temporary skill library."""
    library_dir = tmp_path / "skills"
    library_dir.mkdir()
    return library_dir


@pytest.fixture
def mock_skill():
    """Create a mock skill for testing."""
    return {
        "name": "test_skill",
        "version": "1.0.0",
        "description": "A test skill",
        "author": "test_author"
    }
