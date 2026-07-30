"""Neo4j graph database interface."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

try:
    from neo4j import GraphDatabase, Driver, Session
    HAS_NEO4J = True
except ImportError:
    HAS_NEO4J = False
    Driver = Any
    Session = Any

from .config import Neo4jConfig


class GraphDB:
    """Neo4j graph database wrapper."""
    
    def __init__(self, config: Neo4jConfig):
        if not HAS_NEO4J:
            raise ImportError(
                "neo4j package is required. Install with: pip install neo4j"
            )
        self.config = config
        self._driver: Driver | None = None
    
    @property
    def driver(self) -> Driver:
        """Get or create driver instance."""
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.config.uri,
                auth=(self.config.username, self.config.password)
            )
        return self._driver
    
    def close(self) -> None:
        """Close database connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
    
    @contextmanager
    def session(self) -> Iterator[Session]:
        """Context manager for database session."""
        session = self.driver.session(database=self.config.database)
        try:
            yield session
        finally:
            session.close()
    
    def init_schema(self) -> None:
        """Initialize database schema with constraints and indexes."""
        with self.session() as session:
            # Constraints for unique identifiers
            session.run("CREATE CONSTRAINT file_path IF NOT EXISTS FOR (f:File) REQUIRE f.path IS UNIQUE")
            session.run("CREATE CONSTRAINT class_id IF NOT EXISTS FOR (c:Class) REQUIRE c.id IS UNIQUE")
            session.run("CREATE CONSTRAINT function_id IF NOT EXISTS FOR (f:Function) REQUIRE f.id IS UNIQUE")
            session.run("CREATE CONSTRAINT package_id IF NOT EXISTS FOR (p:Package) REQUIRE p.id IS UNIQUE")
            
            # Indexes for common queries
            session.run("CREATE INDEX file_language IF NOT EXISTS FOR (f:File) ON (f.language)")
            session.run("CREATE INDEX function_name IF NOT EXISTS FOR (f:Function) ON (f.name)")
            session.run("CREATE INDEX class_name IF NOT EXISTS FOR (c:Class) ON (c.name)")
            
            # Full-text search indexes
            session.run(
                "CREATE FULLTEXT INDEX function_search IF NOT EXISTS "
                "FOR (f:Function) ON EACH [f.name, f.docstring]"
            )
            session.run(
                "CREATE FULLTEXT INDEX class_search IF NOT EXISTS "
                "FOR (c:Class) ON EACH [c.name, c.docstring]"
            )
    
    def clear_all(self) -> None:
        """Clear all nodes and relationships. Use with caution!"""
        with self.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def get_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        with self.session() as session:
            result = session.run("""
                MATCH (n)
                WITH labels(n) AS labels, count(*) AS count
                UNWIND labels AS label
                RETURN label, sum(count) AS total
                ORDER BY total DESC
            """)
            node_counts = {record["label"]: record["total"] for record in result}
            
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) AS rel_type, count(*) AS count
                ORDER BY count DESC
            """)
            rel_counts = {record["rel_type"]: record["count"] for record in result}
            
            return {
                "nodes": node_counts,
                "relationships": rel_counts,
                "total_nodes": sum(node_counts.values()),
                "total_relationships": sum(rel_counts.values()),
            }
    
    def create_file_node(self, path: str, language: str, size: int, checksum: str) -> None:
        """Create or update a file node."""
        with self.session() as session:
            session.run("""
                MERGE (f:File {path: $path})
                SET f.language = $language,
                    f.size = $size,
                    f.checksum = $checksum,
                    f.updated_at = datetime()
            """, path=path, language=language, size=size, checksum=checksum)
    
    def create_function_node(
        self,
        id: str,
        name: str,
        path: str,
        line_start: int,
        line_end: int,
        language: str,
        parameters: list[str] | None = None,
        return_type: str | None = None,
        docstring: str | None = None,
        is_public: bool = True,
    ) -> None:
        """Create or update a function node."""
        with self.session() as session:
            session.run("""
                MERGE (f:Function {id: $id})
                SET f.name = $name,
                    f.path = $path,
                    f.line_start = $line_start,
                    f.line_end = $line_end,
                    f.language = $language,
                    f.parameters = $parameters,
                    f.return_type = $return_type,
                    f.docstring = $docstring,
                    f.is_public = $is_public,
                    f.updated_at = datetime()
            """, id=id, name=name, path=path, line_start=line_start, line_end=line_end,
                language=language, parameters=parameters or [], return_type=return_type,
                docstring=docstring, is_public=is_public)
    
    def create_class_node(
        self,
        id: str,
        name: str,
        path: str,
        line_start: int,
        line_end: int,
        language: str,
        docstring: str | None = None,
        is_abstract: bool = False,
    ) -> None:
        """Create or update a class node."""
        with self.session() as session:
            session.run("""
                MERGE (c:Class {id: $id})
                SET c.name = $name,
                    c.path = $path,
                    c.line_start = $line_start,
                    c.line_end = $line_end,
                    c.language = $language,
                    c.docstring = $docstring,
                    c.is_abstract = $is_abstract,
                    c.updated_at = datetime()
            """, id=id, name=name, path=path, line_start=line_start, line_end=line_end,
                language=language, docstring=docstring, is_abstract=is_abstract)
    
    def create_relationship(self, from_id: str, to_id: str, rel_type: str) -> None:
        """Create a relationship between two nodes."""
        with self.session() as session:
            session.run(f"""
                MATCH (a {{id: $from_id}}), (b {{id: $to_id}})
                MERGE (a)-[r:{rel_type}]->(b)
                SET r.created_at = datetime()
            """, from_id=from_id, to_id=to_id)
    
    def delete_file_subgraph(self, path: str) -> None:
        """Delete a file node and all its contained nodes."""
        with self.session() as session:
            session.run("""
                MATCH (f:File {path: $path})
                OPTIONAL MATCH (f)-[:CONTAINS]->(n)
                DETACH DELETE f, n
            """, path=path)
