"""Shared pytest fixtures for ModelMCP tests."""

import pytest
from pathlib import Path


@pytest.fixture
def temp_mcp_dir(tmp_path):
    """Create a temporary MCP server directory."""
    mcp_dir = tmp_path / "mcp_test"
    mcp_dir.mkdir()
    return mcp_dir


@pytest.fixture
def mock_mcp_config():
    """Mock MCP server configuration."""
    return {
        "name": "test-mcp",
        "version": "0.1.0",
        "entry_point": "server.py",
    }
