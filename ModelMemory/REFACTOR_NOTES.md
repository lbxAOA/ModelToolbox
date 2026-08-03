# ModelMemory Refactor Requirements

This document captures additional requirements beyond the main specification.

## Dependencies

### Required Python Packages
```
neo4j>=5.0.0
tree-sitter>=0.21.0
tree-sitter-python>=0.21.0
tree-sitter-javascript>=0.21.0
tree-sitter-typescript>=0.21.0
```

### Optional Dependencies
```
sentence-transformers>=2.0.0  # For local embeddings
mcp>=0.1.0  # For MCP server
```

## Installation Notes

Users need to:
1. Install Neo4j (local or cloud)
2. Install Python dependencies
3. Configure Neo4j connection in config.json
4. Run `mtb memory init` to initialize schema

## Migration from Old Version

The old `index.py` implementation used SQLite FTS5 for simple text search. The new implementation:

1. **Replaces**: SQLite with Neo4j graph database
2. **Adds**: Tree-sitter based code parsing
3. **Adds**: Structured code relationships (calls, imports, inheritance)
4. **Adds**: MCP server for AI agent integration
5. **Keeps**: CLI interface (with new commands)

### Breaking Changes

- Old commands renamed:
  - `mtb memory index` → `mtb memory parse`
  - Database location changed from SQLite to Neo4j
  - Search results format changed (now includes code nodes)

### Migration Script

Users can run both systems side-by-side. No automatic migration provided.

## Feature Implementation Status

✅ Implemented:
- Configuration management
- Neo4j graph database integration
- Tree-sitter parser (Python support)
- Basic code node extraction (functions, classes)
- Full-text search via Neo4j
- CLI commands (init, parse, search, stats)
- Python API (CodeGraph class)
- MCP server skeleton

⏳ Partially Implemented:
- JavaScript/TypeScript parsing (structure ready, needs implementation)
- Relationship extraction (CONTAINS only)

❌ Not Yet Implemented:
- Call relationship detection
- Import relationship detection
- Inheritance/implements relationships
- Semantic search (embeddings)
- Impact analysis
- Community detection
- Execution flow analysis
- Test coverage analysis
- Change analysis
- Web dashboard

## Next Steps

Priority order for completing the implementation:

1. **Relationship Extraction** (High Priority)
   - Detect function calls
   - Detect imports
   - Detect class inheritance

2. **Impact Analysis** (High Priority)
   - Traverse call graph
   - Find affected code
   - Calculate impact levels

3. **JavaScript/TypeScript Support** (Medium Priority)
   - Implement JS/TS parsing
   - Extract nodes and relationships

4. **Semantic Search** (Medium Priority)
   - Integrate sentence-transformers
   - Generate embeddings for functions/classes
   - Vector similarity search

5. **Advanced Features** (Low Priority)
   - Community detection
   - Test coverage analysis
   - Web dashboard

## Testing Strategy

1. **Unit Tests**: Test individual components (parser, config, models)
2. **Integration Tests**: Test with real Neo4j instance
3. **End-to-End Tests**: Test full CLI workflows
4. **Performance Tests**: Test on large codebases (100K+ lines)

## Performance Considerations

- Parsing is CPU-bound (tree-sitter is fast)
- Neo4j write performance depends on batch size
- Consider batching node/relationship creation
- Use transactions for consistency
- Index critical fields for query performance

## Security Notes

- Neo4j credentials should be stored securely
- Consider using environment variables for passwords
- API keys for embedding services should not be committed
- Default password should be changed in production
