"""MCP server for ModelMemory - Code knowledge graph."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent

from .api import CodeGraph
from .config import MemoryConfig


# Create MCP server instance
server = Server("modeltoolbox-memory")

# Global graph instance
_graph: CodeGraph | None = None


def get_graph() -> CodeGraph:
    """Get or create the graph instance."""
    global _graph
    if _graph is None:
        config = MemoryConfig.load(MemoryConfig.default_config_path())
        _graph = CodeGraph(config)
    return _graph


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="search_code",
            description="Search for code using full-text search. Returns functions and classes matching the query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords or phrases)",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="analyze_impact",
            description="Analyze the impact of changing a function or class. Shows what code would be affected.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path",
                    },
                    "name": {
                        "type": "string",
                        "description": "Function or class name (optional)",
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="get_call_graph",
            description="Get the call graph for a function. Shows what functions it calls and what calls it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_id": {
                        "type": "string",
                        "description": "Function identifier (path::name:line)",
                    },
                    "depth": {
                        "type": "number",
                        "description": "Maximum depth to traverse",
                        "default": 2,
                    },
                },
                "required": ["function_id"],
            },
        ),
        Tool(
            name="find_tests",
            description="Find test functions for a given function or class.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Function or class name to find tests for",
                    },
                },
                "required": ["target"],
            },
        ),
        Tool(
            name="analyze_changes",
            description="Analyze code changes (e.g., from a git diff) and show impact.",
            inputSchema={
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of changed file paths",
                    },
                },
                "required": ["files"],
            },
        ),
        Tool(
            name="get_stats",
            description="Get graph statistics (node counts, relationship counts).",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from MCP clients."""
    graph = get_graph()
    
    try:
        if name == "search_code":
            query = arguments["query"]
            limit = arguments.get("limit", 10)
            results = graph.search(query, limit=limit)
            
            response = {
                "query": query,
                "count": len(results),
                "results": [
                    {
                        "name": r.node.name,
                        "type": r.node.node_type.value,
                        "path": r.node.path,
                        "line": r.node.line_start,
                        "score": r.score,
                        "snippet": r.snippet,
                    }
                    for r in results
                ],
            }
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
        elif name == "analyze_impact":
            path = arguments["path"]
            func_name = arguments.get("name")
            
            try:
                analysis = graph.analyze_impact(path, func_name)
                response = {
                    "target": {
                        "name": analysis.target.name,
                        "path": analysis.target.path,
                    },
                    "direct_impacts": len(analysis.direct_impacts),
                    "indirect_impacts": len(analysis.indirect_impacts),
                    "total_impacts": analysis.total_impacts,
                }
                return [TextContent(type="text", text=json.dumps(response, indent=2))]
            except NotImplementedError:
                return [TextContent(type="text", text="Impact analysis not yet implemented")]
        
        elif name == "get_call_graph":
            return [TextContent(type="text", text="Call graph analysis not yet implemented")]
        
        elif name == "find_tests":
            return [TextContent(type="text", text="Test discovery not yet implemented")]
        
        elif name == "analyze_changes":
            files = arguments["files"]
            stats = graph.update([Path(f) for f in files])
            response = {
                "updated": stats["updated"],
                "failed": stats["failed"],
            }
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
        elif name == "get_stats":
            stats = graph.get_stats()
            return [TextContent(type="text", text=json.dumps(stats, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
