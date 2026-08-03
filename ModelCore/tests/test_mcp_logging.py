"""Tests for modeltoolbox_core.mcp_logging module."""
import pytest
from modeltoolbox_core.mcp_logging import (
    setup_mcp_logger,
    log_tool_call,
    create_health_check_tool
)


def test_setup_mcp_logger():
    """Test MCP logger setup."""
    logger = setup_mcp_logger("test_server", level="DEBUG")
    assert logger.name == "mcp.test_server"


def test_log_tool_call_decorator():
    """Test tool call logging decorator."""
    @log_tool_call
    def sample_tool(param: str) -> dict:
        return {"result": param}
    
    result = sample_tool("test_value")
    assert result == {"result": "test_value"}


def test_log_tool_call_with_exception():
    """Test tool call decorator with exception."""
    @log_tool_call
    def failing_tool():
        raise ValueError("tool failed")
    
    with pytest.raises(ValueError, match="tool failed"):
        failing_tool()


def test_log_tool_call_preserves_metadata():
    """Test decorator preserves function metadata."""
    @log_tool_call
    def documented_tool(x: int) -> int:
        """A documented tool."""
        return x * 2
    
    assert documented_tool.__name__ == "documented_tool"
    assert documented_tool.__doc__ == "A documented tool."


def test_create_health_check_tool():
    """Test health check tool creation."""
    def check_deps():
        return {"git": True, "node": False}
    
    health_check = create_health_check_tool(
        server_name="test_server",
        version="1.0.0",
        check_dependencies=check_deps
    )
    
    result = health_check()
    
    assert result["status"] == "degraded"
    assert result["server"] == "test_server"
    assert result["version"] == "1.0.0"
    assert result["dependencies"]["git"] is True
    assert result["dependencies"]["node"] is False


def test_create_health_check_tool_all_healthy():
    """Test health check with all dependencies available."""
    def check_deps():
        return {"git": True, "node": True}
    
    health_check = create_health_check_tool(
        server_name="healthy_server",
        version="2.0.0",
        check_dependencies=check_deps
    )
    
    result = health_check()
    assert result["status"] == "healthy"
