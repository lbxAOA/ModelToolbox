"""Shared pytest fixtures for ModelProvider tests."""
import pytest
from pathlib import Path


@pytest.fixture
def tmp_provider_config(tmp_path):
    """Create a temporary provider configuration."""
    config_dir = tmp_path / ".modeltoolbox"
    config_dir.mkdir()
    return {
        "providers": {},
        "active_provider": None,
        "config_dir": config_dir
    }


@pytest.fixture
def mock_provider():
    """Create a mock provider for testing."""
    return {
        "name": "test_provider",
        "type": "openai",
        "api_key": "test-key-123",
        "model": "gpt-4"
    }
