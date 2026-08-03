"""MCP server logging utilities for ModelToolbox.

Provides decorators and tools for MCP server monitoring.
"""
import time
import functools
from typing import Callable, Any, TypeVar, Dict
from .logging import get_logger

T = TypeVar('T')


def setup_mcp_logger(server_name: str, level: str = "INFO") -> Any:
    """Setup logger for an MCP server.
    
    Args:
        server_name: Name of the MCP server
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    return get_logger(f"mcp.{server_name}", level)


def log_tool_call(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to log MCP tool calls with timing.
    
    Usage:
        @mcp.tool()
        @log_tool_call
        def my_tool(param: str) -> dict:
            return {"result": "success"}
    """
    logger = get_logger(f"mcp.tool.{func.__name__}")
    
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        start = time.perf_counter()
        
        logger.info(f"Tool call: {func.__name__}")
        logger.debug(f"Arguments: args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(f"Tool {func.__name__} completed in {duration_ms:.1f}ms")
            return result
        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(
                f"Tool {func.__name__} failed after {duration_ms:.1f}ms: {e}",
                exc_info=True
            )
            raise
    
    return wrapper


def create_health_check_tool(
    server_name: str,
    version: str,
    check_dependencies: Callable[[], Dict[str, bool]]
) -> Callable[[], Dict[str, Any]]:
    """Create a health_check tool for an MCP server.
    
    Args:
        server_name: Name of the server
        version: Server version
        check_dependencies: Function that returns dependency status dict
    
    Returns:
        Health check function ready to be registered as MCP tool
    """
    def health_check() -> Dict[str, Any]:
        """Check server health and dependencies."""
        deps = check_dependencies()
        all_healthy = all(deps.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "server": server_name,
            "version": version,
            "dependencies": deps
        }
    
    return health_check
