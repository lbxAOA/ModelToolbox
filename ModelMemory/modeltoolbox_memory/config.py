"""ModelMemory configuration management."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from modeltoolbox_core.config import default_config
from modeltoolbox_core.jsonio import load_json, dump_json


@dataclass
class Neo4jConfig:
    """Neo4j database configuration."""
    uri: str = "bolt://localhost:7687"
    username: str = "neo4j"
    password: str = "password"
    database: str = "neo4j"


@dataclass
class EmbeddingConfig:
    """Embedding model configuration."""
    provider: Literal["local", "openai", "google"] = "local"
    model: str = "all-MiniLM-L6-v2"
    api_key: str | None = None
    batch_size: int = 32


@dataclass
class ParserConfig:
    """Code parser configuration."""
    languages: list[str] = field(default_factory=lambda: ["python", "javascript", "typescript"])
    max_file_size: int = 1024 * 1024  # 1MB
    skip_dirs: set[str] = field(default_factory=lambda: {
        ".git", ".hg", ".svn", "__pycache__", "node_modules",
        ".venv", "venv", "dist", "build", ".pytest_cache",
        ".mypy_cache", ".ruff_cache", ".modeltoolbox"
    })


@dataclass
class MemoryConfig:
    """ModelMemory configuration."""
    neo4j: Neo4jConfig = field(default_factory=Neo4jConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    parser: ParserConfig = field(default_factory=ParserConfig)
    project_root: Path | None = None
    
    @classmethod
    def load(cls, path: Path | None = None) -> MemoryConfig:
        """Load configuration from file or use defaults."""
        if path and path.exists():
            data = load_json(path)
            return cls(
                neo4j=Neo4jConfig(**data.get("neo4j", {})),
                embedding=EmbeddingConfig(**data.get("embedding", {})),
                parser=ParserConfig(**data.get("parser", {})),
                project_root=Path(data["project_root"]) if "project_root" in data else None,
            )
        return cls()
    
    def save(self, path: Path) -> None:
        """Save configuration to file."""
        data = {
            "neo4j": {
                "uri": self.neo4j.uri,
                "username": self.neo4j.username,
                "password": self.neo4j.password,
                "database": self.neo4j.database,
            },
            "embedding": {
                "provider": self.embedding.provider,
                "model": self.embedding.model,
                "api_key": self.embedding.api_key,
                "batch_size": self.embedding.batch_size,
            },
            "parser": {
                "languages": self.parser.languages,
                "max_file_size": self.parser.max_file_size,
                "skip_dirs": list(self.parser.skip_dirs),
            },
        }
        if self.project_root:
            data["project_root"] = str(self.project_root)
        dump_json(data, path)
    
    @classmethod
    def default_config_path(cls, root: Path | None = None) -> Path:
        """Get default configuration file path."""
        config = default_config(root)
        return config.state_dir / "memory" / "config.json"
