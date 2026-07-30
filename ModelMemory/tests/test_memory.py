"""Tests for ModelMemory core functionality."""

import pytest
from pathlib import Path

from modeltoolbox_memory import CodeGraph, MemoryConfig
from modeltoolbox_memory.models import NodeType, RelationType


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary test project."""
    # Create a simple Python file
    test_file = tmp_path / "test_module.py"
    test_file.write_text('''
"""Test module."""

def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

class Calculator:
    """Simple calculator."""
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    
    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b
''')
    return tmp_path


@pytest.fixture
def graph(temp_project):
    """Create a CodeGraph instance."""
    config = MemoryConfig()
    config.project_root = temp_project
    graph = CodeGraph(config)
    yield graph
    graph.close()


def test_config_creation():
    """Test configuration creation."""
    config = MemoryConfig()
    assert config.neo4j.uri == "bolt://localhost:7687"
    assert config.embedding.provider == "local"
    assert "python" in config.parser.languages


def test_config_save_load(tmp_path):
    """Test configuration save and load."""
    config = MemoryConfig()
    config.project_root = tmp_path
    
    config_path = tmp_path / "config.json"
    config.save(config_path)
    
    loaded = MemoryConfig.load(config_path)
    assert loaded.project_root == tmp_path


def test_parser_detect_language():
    """Test language detection from file extension."""
    from modeltoolbox_memory.parser import CodeParser
    
    parser = CodeParser()
    assert parser._detect_language(Path("test.py")) == "python"
    assert parser._detect_language(Path("test.js")) == "javascript"
    assert parser._detect_language(Path("test.ts")) == "typescript"
    assert parser._detect_language(Path("test.txt")) is None


def test_parse_simple_file(temp_project):
    """Test parsing a simple Python file."""
    from modeltoolbox_memory.parser import CodeParser
    
    parser = CodeParser()
    test_file = temp_project / "test_module.py"
    
    result = parser.parse_file(test_file, "python")
    
    assert result is not None
    assert result.language == "python"
    assert len(result.nodes) > 0
    
    # Check for function node
    func_nodes = [n for n in result.nodes if n.node_type == NodeType.FUNCTION]
    assert len(func_nodes) >= 1
    
    # Check for class node
    class_nodes = [n for n in result.nodes if n.node_type == NodeType.CLASS]
    assert len(class_nodes) >= 1


def test_graph_initialization(graph):
    """Test graph initialization."""
    # This would require a running Neo4j instance
    # For now, just check that the graph object is created
    assert graph is not None
    assert graph.config is not None


def test_node_types():
    """Test node type enumerations."""
    assert NodeType.FILE.value == "File"
    assert NodeType.FUNCTION.value == "Function"
    assert NodeType.CLASS.value == "Class"


def test_relationship_types():
    """Test relationship type enumerations."""
    assert RelationType.CONTAINS.value == "CONTAINS"
    assert RelationType.CALLS.value == "CALLS"
    assert RelationType.IMPORTS.value == "IMPORTS"


# Integration tests (require Neo4j)

@pytest.mark.integration
def test_full_parse_flow(graph, temp_project):
    """Test full parsing flow (requires Neo4j)."""
    try:
        graph.init()
        stats = graph.parse(temp_project)
        
        assert stats["files"] > 0
        assert stats["nodes"] > 0
        
        # Test search
        results = graph.search("hello")
        assert len(results) > 0
        
    except ImportError:
        pytest.skip("Neo4j not available")


@pytest.mark.integration
def test_update_flow(graph, temp_project):
    """Test incremental update flow (requires Neo4j)."""
    try:
        graph.init()
        graph.parse(temp_project)
        
        # Modify file
        test_file = temp_project / "test_module.py"
        test_file.write_text(test_file.read_text() + "\n\ndef new_func():\n    pass\n")
        
        # Update
        stats = graph.update([test_file])
        assert stats["updated"] == 1
        
    except ImportError:
        pytest.skip("Neo4j not available")
