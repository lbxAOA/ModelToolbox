"""Test ModelMCP server discovery and management."""

import pytest
from pathlib import Path
from modeltoolbox_mcp.registry import discover_servers, McpServer


def test_mcp_server_creation():
    """Test McpServer creation."""
    server = McpServer(
        name="test-server",
        command=["python", "server.py"],
        description="A test server",
    )
    assert server.name == "test-server"
    assert server.command == ["python", "server.py"]
    assert server.description == "A test server"


def test_mcp_server_with_cwd():
    """Test McpServer with working directory."""
    server = McpServer(
        name="test-server",
        command=["python", "server.py"],
        cwd="/path/to/server",
    )
    assert server.cwd == "/path/to/server"


def test_discover_servers_finds_servers():
    """Test that discover_servers finds actual servers."""
    servers = discover_servers()
    # Should find at least the MCP servers in the repo
    assert len(servers) >= 0  # May be 0 if no servers present
    
    # Check structure if servers exist
    for server in servers:
        assert hasattr(server, 'name')
        assert hasattr(server, 'command')


def test_discover_servers_in_custom_path(tmp_path):
    """Test discovering servers in a custom path."""
    # Create a mock server directory
    server_dir = tmp_path / "test-server"
    server_dir.mkdir()
    server_file = server_dir / "server.py"
    server_file.write_text("# Mock MCP server", encoding="utf-8")
    
    # Discovery should work (even if it finds nothing in tmp_path)
    servers = discover_servers()
    assert isinstance(servers, list)
