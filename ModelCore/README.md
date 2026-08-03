# ModelCore

Core utilities for ModelToolbox: logging, telemetry, configuration, and plugin system.

## Features

- **Unified Logging**: Zero-configuration structured logging with console and file outputs
- **Performance Monitoring**: Decorators for tracking command execution time and errors
- **Health Checks**: Dependency checking and version information reporting
- **MCP Server Support**: Specialized logging and monitoring for MCP servers
- **Plugin System**: Dynamic plugin loading via entry points

## Installation

```bash
pip install modeltoolbox-core
```

For development:

```bash
pip install -e "ModelCore[dev]"
```

## Usage

### Logging

```python
from modeltoolbox_core.logging import get_logger

logger = get_logger(__name__)
logger.info("Processing started")
logger.error("An error occurred", exc_info=True)
```

Logs are written to:
- Console: `INFO` level and above
- File: `~/.modeltoolbox/logs/modeltoolbox-YYYY-MM-DD.log` (all levels, JSON format)
- Errors: `~/.modeltoolbox/logs/errors-YYYY-MM-DD.log` (ERROR level only)

### Performance Tracking

```python
from modeltoolbox_core.telemetry import track_performance

@track_performance
def expensive_operation():
    # Your code here
    pass
```

### Health Checks

```python
from modeltoolbox_core.health import health_check

status = health_check()
print(status)
# {
#   "status": "healthy",
#   "version_info": {"python": "3.11.0", ...},
#   "dependencies": {"git": {"available": True, "version": "..."}, ...}
# }
```

### MCP Server Integration

```python
from mcp.server.fastmcp import FastMCP
from modeltoolbox_core.mcp_logging import setup_mcp_logger, log_tool_call

logger = setup_mcp_logger("my_server")
mcp = FastMCP("my_server")

@mcp.tool()
@log_tool_call
def my_tool(param: str) -> dict:
    """My tool with automatic logging."""
    return {"result": param}
```

## Testing

```bash
pytest ModelCore/tests/
```

## License

MIT
