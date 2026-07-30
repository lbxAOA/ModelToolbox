"""Core CodeGraph API for analyzing codebases."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Iterator

from .config import MemoryConfig
from .graph import GraphDB
from .parser import CodeParser, ParsedFile
from .models import CodeNode, ImpactAnalysis, SearchResult


class CodeGraph:
    """Main API for code graph operations."""
    
    def __init__(self, config: MemoryConfig | None = None):
        self.config = config or MemoryConfig()
        self.db = GraphDB(self.config.neo4j)
        self.parser = CodeParser()
    
    @classmethod
    def from_project(cls, root: Path | str, config: MemoryConfig | None = None) -> CodeGraph:
        """Create a CodeGraph instance for a project."""
        if config is None:
            config = MemoryConfig()
        config.project_root = Path(root).resolve()
        return cls(config)
    
    def close(self) -> None:
        """Close database connection."""
        self.db.close()
    
    def __enter__(self) -> CodeGraph:
        return self
    
    def __exit__(self, *args) -> None:
        self.close()
    
    def init(self) -> None:
        """Initialize the graph database schema."""
        self.db.init_schema()
    
    def parse(
        self,
        root: Path | str | None = None,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> dict[str, int]:
        """Parse codebase and build the graph.
        
        Args:
            root: Root directory to parse (defaults to project_root)
            include: File patterns to include (e.g., ["*.py", "*.js"])
            exclude: File patterns to exclude (e.g., ["tests/*"])
            
        Returns:
            Statistics dictionary with counts
        """
        root_path = Path(root) if root else self.config.project_root
        if not root_path:
            raise ValueError("No root directory specified")
        
        root_path = root_path.resolve()
        
        stats = {
            "files": 0,
            "nodes": 0,
            "relationships": 0,
            "skipped": 0,
            "failed": 0,
        }
        
        # Iterate through files
        for file_path in self._iter_files(root_path, include, exclude):
            try:
                parsed = self.parser.parse_file(file_path)
                if not parsed:
                    stats["skipped"] += 1
                    continue
                
                # Create file node
                self.db.create_file_node(
                    path=parsed.path,
                    language=parsed.language,
                    size=file_path.stat().st_size,
                    checksum=parsed.checksum,
                )
                stats["files"] += 1
                
                # Create code nodes
                for node in parsed.nodes:
                    if node.node_type.value == "Function":
                        func = node
                        self.db.create_function_node(
                            id=func.id,
                            name=func.name,
                            path=func.path,
                            line_start=func.line_start,
                            line_end=func.line_end,
                            language=func.language,
                            parameters=getattr(func, "parameters", []),
                            return_type=getattr(func, "return_type", None),
                            docstring=getattr(func, "docstring", None),
                            is_public=getattr(func, "is_public", True),
                        )
                    elif node.node_type.value == "Class":
                        cls = node
                        self.db.create_class_node(
                            id=cls.id,
                            name=cls.name,
                            path=cls.path,
                            line_start=cls.line_start,
                            line_end=cls.line_end,
                            language=cls.language,
                            docstring=getattr(cls, "docstring", None),
                        )
                    stats["nodes"] += 1
                
                # Create relationships
                for rel in parsed.relationships:
                    self.db.create_relationship(
                        from_id=rel.from_id,
                        to_id=rel.to_id,
                        rel_type=rel.rel_type.value,
                    )
                    stats["relationships"] += 1
                
            except Exception as e:
                stats["failed"] += 1
                print(f"Failed to parse {file_path}: {e}")
        
        return stats
    
    def update(self, paths: list[Path | str]) -> dict[str, int]:
        """Incrementally update the graph for changed files.
        
        Args:
            paths: List of file paths that changed
            
        Returns:
            Statistics dictionary with counts
        """
        stats = {"updated": 0, "failed": 0}
        
        for path in paths:
            file_path = Path(path)
            try:
                # Delete old subgraph
                self.db.delete_file_subgraph(file_path.as_posix())
                
                # Re-parse file
                parsed = self.parser.parse_file(file_path)
                if not parsed:
                    stats["failed"] += 1
                    continue
                
                # Re-create nodes (similar to parse method)
                self.db.create_file_node(
                    path=parsed.path,
                    language=parsed.language,
                    size=file_path.stat().st_size,
                    checksum=parsed.checksum,
                )
                
                for node in parsed.nodes:
                    if node.node_type.value == "Function":
                        func = node
                        self.db.create_function_node(
                            id=func.id,
                            name=func.name,
                            path=func.path,
                            line_start=func.line_start,
                            line_end=func.line_end,
                            language=func.language,
                            parameters=getattr(func, "parameters", []),
                            return_type=getattr(func, "return_type", None),
                            docstring=getattr(func, "docstring", None),
                            is_public=getattr(func, "is_public", True),
                        )
                    elif node.node_type.value == "Class":
                        cls = node
                        self.db.create_class_node(
                            id=cls.id,
                            name=cls.name,
                            path=cls.path,
                            line_start=cls.line_start,
                            line_end=cls.line_end,
                            language=cls.language,
                            docstring=getattr(cls, "docstring", None),
                        )
                
                for rel in parsed.relationships:
                    self.db.create_relationship(
                        from_id=rel.from_id,
                        to_id=rel.to_id,
                        rel_type=rel.rel_type.value,
                    )
                
                stats["updated"] += 1
                
            except Exception as e:
                stats["failed"] += 1
                print(f"Failed to update {path}: {e}")
        
        return stats
    
    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Search for code using full-text search.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        results = []
        
        with self.db.session() as session:
            # Search functions
            func_results = session.run("""
                CALL db.index.fulltext.queryNodes('function_search', $query)
                YIELD node, score
                RETURN node, score
                LIMIT $limit
            """, query=query, limit=limit)
            
            for record in func_results:
                node_data = dict(record["node"])
                results.append(SearchResult(
                    node=CodeNode(
                        id=node_data["id"],
                        name=node_data["name"],
                        path=node_data["path"],
                        line_start=node_data["line_start"],
                        line_end=node_data["line_end"],
                        language=node_data["language"],
                        node_type="Function",
                    ),
                    score=record["score"],
                    snippet=node_data.get("docstring", ""),
                ))
        
        return sorted(results, key=lambda r: r.score, reverse=True)[:limit]
    
    def search_semantic(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Search for code using semantic similarity (requires embeddings).
        
        Args:
            query: Natural language query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        # TODO: Implement embedding-based semantic search
        raise NotImplementedError("Semantic search requires embedding implementation")
    
    def analyze_impact(self, path: str, name: str | None = None) -> ImpactAnalysis:
        """Analyze the impact of changing a function or class.
        
        Args:
            path: File path
            name: Function or class name (optional)
            
        Returns:
            Impact analysis result
        """
        # TODO: Implement full impact analysis
        raise NotImplementedError("Impact analysis not yet implemented")
    
    def get_stats(self) -> dict:
        """Get graph statistics."""
        return self.db.get_stats()
    
    def _iter_files(
        self,
        root: Path,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> Iterator[Path]:
        """Iterate through files in the root directory."""
        skip_dirs = self.config.parser.skip_dirs
        
        for path in root.rglob("*"):
            # Skip directories in skip list
            if any(part in skip_dirs for part in path.parts):
                continue
            
            # Only process files
            if not path.is_file():
                continue
            
            # Check size limit
            try:
                if path.stat().st_size > self.config.parser.max_file_size:
                    continue
            except OSError:
                continue
            
            # Check include/exclude patterns
            # TODO: Implement pattern matching
            
            # Check if language is supported
            if self.parser._detect_language(path):
                yield path
