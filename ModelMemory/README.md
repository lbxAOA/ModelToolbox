# ModelMemory

Code knowledge graph system for understanding and analyzing codebases.

## Features

- **Code Parsing**: Parse Python, JavaScript, and TypeScript codebases using tree-sitter
- **Graph Database**: Store code structure in Neo4j for powerful relationship queries
- **Full-Text Search**: Search for functions, classes, and code patterns
- **Semantic Search**: Find code by meaning (requires embedding configuration)
- **Impact Analysis**: Understand what code would be affected by changes
- **CLI & Python API**: Use from command line or integrate into your tools
- **MCP Server**: Expose to AI agents like Claude

## Installation

### Requirements

1. **Python 3.11+**
2. **Neo4j Database** (local or remote)
   - Download from: https://neo4j.com/download/
   - Or run with Docker: `docker run -p 7687:7687 -p 7474:7474 neo4j`

### Install Dependencies

```bash
pip install neo4j tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript
```

Or install the full ModelToolbox:

```bash
pip install -e .
```

## Quick Start

### 1. Initialize ModelMemory

```bash
# Initialize for current project
mtb memory init .

# Initialize for a specific project
mtb memory init /path/to/project
```

### 2. Parse Your Codebase

```bash
# Parse all supported files
mtb memory parse .

# Parse specific file types
mtb memory parse . --include "*.py" --include "*.ts"

# Exclude directories
mtb memory parse . --exclude "tests/*" --exclude "node_modules/*"
```

### 3. Search Your Code

```bash
# Full-text search
mtb memory search "authentication"

# Semantic search (requires embeddings)
mtb memory search-semantic "user login logic"

# View graph statistics
mtb memory stats
```

## Configuration

Configuration is stored in `~/.modeltoolbox/state/memory/config.json`:

```json
{
  "neo4j": {
    "uri": "bolt://localhost:7687",
    "username": "neo4j",
    "password": "password",
    "database": "neo4j"
  },
  "embedding": {
    "provider": "local",
    "model": "all-MiniLM-L6-v2"
  },
  "parser": {
    "languages": ["python", "javascript", "typescript"],
    "max_file_size": 1048576
  }
}
```

## Python API

```python
from modeltoolbox_memory import CodeGraph

# Create graph for a project
graph = CodeGraph.from_project("./my-project")

# Initialize database schema
graph.init()

# Parse the codebase
stats = graph.parse(include=["*.py"])
print(f"Parsed {stats['files']} files, {stats['nodes']} nodes")

# Search for code
results = graph.search("authentication")
for result in results:
    print(f"{result.node.name} in {result.node.path}:{result.node.line_start}")

# Get statistics
stats = graph.get_stats()
print(f"Total nodes: {stats['total_nodes']}")
print(f"Total relationships: {stats['total_relationships']}")

# Clean up
graph.close()
```

## MCP Server

ModelMemory can be used as an MCP server for AI agents:

### Start Server

```bash
mtb memory serve-mcp
```

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "modeltoolbox-memory": {
      "command": "mtb",
      "args": ["memory", "serve-mcp"]
    }
  }
}
```

### Available MCP Tools

- `search_code`: Search for functions and classes
- `analyze_impact`: Analyze impact of changes
- `get_call_graph`: Get function call relationships
- `find_tests`: Find test functions
- `analyze_changes`: Analyze code changes
- `get_stats`: Get graph statistics

## CLI Commands

### Core Commands

```bash
# Initialize project
mtb memory init [path]

# Parse codebase
mtb memory parse [path] [--include PATTERN] [--exclude PATTERN]

# Update changed files
mtb memory update file1.py file2.py

# Search
mtb memory search "query" [--limit 10]
mtb memory search-semantic "natural language query"

# Statistics
mtb memory stats [--json]

# Impact analysis
mtb memory impact path/to/file.py [--name function_name]
```

## Architecture

ModelMemory consists of several key components:

### Parser (`parser.py`)
- Uses tree-sitter for language parsing
- Extracts functions, classes, and relationships
- Supports Python, JavaScript, TypeScript (extensible)

### Graph Database (`graph.py`)
- Neo4j integration for graph storage
- Schema management and indexing
- Query optimization

### API (`api.py`)
- High-level Python API
- Search functionality
- Impact analysis (planned)
- Community detection (planned)

### CLI (`cli.py`)
- Command-line interface
- JSON output support
- Integration with other tools

### MCP Server (`mcp_server.py`)
- Model Context Protocol implementation
- Tool definitions for AI agents
- Async operation support

## Supported Languages

Currently supported:
- Python (.py)
- JavaScript (.js, .jsx)
- TypeScript (.ts, .tsx)

Planned:
- Java
- Go
- C/C++
- Rust

## Troubleshooting

### Neo4j Connection Issues

```bash
# Check if Neo4j is running
curl http://localhost:7474/

# Test connection
python -c "from neo4j import GraphDatabase; GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))"
```

### Missing Dependencies

```bash
# Install tree-sitter packages
pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript

# Install Neo4j driver
pip install neo4j
```

## Development

### Run Tests

```bash
pytest tests/test_memory.py

# Run integration tests (requires Neo4j)
pytest tests/test_memory.py -m integration
```

### Project Structure

```
ModelMemory/
├── modeltoolbox_memory/
│   ├── __init__.py      # Package exports
│   ├── api.py           # CodeGraph API
│   ├── cli.py           # CLI commands
│   ├── config.py        # Configuration
│   ├── graph.py         # Neo4j integration
│   ├── models.py        # Data models
│   ├── parser.py        # Tree-sitter parser
│   └── mcp_server.py    # MCP server
├── tests/
│   └── test_memory.py   # Tests
└── README.md
```

## License

MIT - See LICENSE file for details
