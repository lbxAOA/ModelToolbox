# ModelMCP

MCP server management and registry for ModelToolbox.

## Structure

```
ModelMCP/
  pyproject.toml           # Aggregator package
  modeltoolbox_mcp/        # Management CLI
  packages/                # Individual MCP servers (future location)
    ltspice-mcp/
    obsidian-rag-mcp/
    altium-mcp/
    ach-roundtable-mcp/
```

## Current Structure (Legacy)

MCP servers are currently in the root directory. They will be moved to `packages/` in Phase 3.

## Individual MCP Servers

### ltspice-mcp (v0.1.0)
LTspice circuit simulation and analysis.

### obsidian-rag-mcp (v0.1.0)
Obsidian vault RAG indexing and search.

### altium-mcp (v0.5.0)
Altium Designer PCB automation.

### ach-roundtable-mcp (v0.5.0)
Multi-agent collaboration using AutoGen.

## Installation

Install the management layer:
```bash
pip install modeltoolbox-mcp
```

Install with specific servers:
```bash
pip install "modeltoolbox-mcp[ltspice,obsidian-rag]"
```

Install all servers:
```bash
pip install "modeltoolbox-mcp[all]"
```

## Usage

### List MCP Servers
```bash
mtb mcp list
```

### Scaffold New Server
```bash
mtb mcp scaffold my-server
```

### Register Server
```bash
mtb mcp register ./my-server
```

## Development

Run tests:
```bash
pytest ModelMCP/tests/
```

## Version History

- **0.5.0**: Unified version for altium-mcp and ach-roundtable-mcp
- **0.2.0**: Management layer with independent packaging
- **0.1.0**: Initial individual server releases

## License

MIT
