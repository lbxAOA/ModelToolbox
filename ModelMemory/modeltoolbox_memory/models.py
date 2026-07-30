"""Data models for code graph nodes and relationships."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeType(str, Enum):
    """Types of nodes in the code graph."""
    FILE = "File"
    PACKAGE = "Package"
    CLASS = "Class"
    FUNCTION = "Function"
    VARIABLE = "Variable"
    TYPE = "Type"
    INTERFACE = "Interface"


class RelationType(str, Enum):
    """Types of relationships in the code graph."""
    CONTAINS = "CONTAINS"
    CALLS = "CALLS"
    IMPORTS = "IMPORTS"
    INHERITS = "INHERITS"
    IMPLEMENTS = "IMPLEMENTS"
    USES = "USES"
    TESTS = "TESTS"


@dataclass
class CodeNode:
    """Base class for all code nodes."""
    id: str
    name: str
    path: str
    line_start: int
    line_end: int
    language: str
    node_type: NodeType


@dataclass
class FileNode(CodeNode):
    """Represents a source file."""
    size: int = 0
    checksum: str = ""
    
    def __post_init__(self):
        self.node_type = NodeType.FILE


@dataclass
class FunctionNode(CodeNode):
    """Represents a function or method."""
    parameters: list[str] = field(default_factory=list)
    return_type: str | None = None
    docstring: str | None = None
    complexity: int = 0
    is_public: bool = True
    
    def __post_init__(self):
        self.node_type = NodeType.FUNCTION


@dataclass
class ClassNode(CodeNode):
    """Represents a class or type definition."""
    methods_count: int = 0
    docstring: str | None = None
    is_abstract: bool = False
    
    def __post_init__(self):
        self.node_type = NodeType.CLASS


@dataclass
class PackageNode(CodeNode):
    """Represents a module or package."""
    
    def __post_init__(self):
        self.node_type = NodeType.PACKAGE


@dataclass
class CodeRelationship:
    """Represents a relationship between two nodes."""
    from_id: str
    to_id: str
    rel_type: RelationType
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Search result with relevance score."""
    node: CodeNode
    score: float
    snippet: str | None = None
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImpactAnalysis:
    """Result of impact analysis."""
    target: CodeNode
    direct_impacts: list[CodeNode]
    indirect_impacts: list[CodeNode]
    potential_impacts: list[CodeNode]
    
    @property
    def total_impacts(self) -> int:
        return len(self.direct_impacts) + len(self.indirect_impacts) + len(self.potential_impacts)
