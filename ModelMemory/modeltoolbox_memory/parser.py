"""Tree-sitter based code parser for multiple languages."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from tree_sitter import Language, Parser, Node as TSNode
    import tree_sitter_python
    import tree_sitter_javascript
    import tree_sitter_typescript
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False
    Language = Any
    Parser = Any
    TSNode = Any

from .models import CodeNode, FunctionNode, ClassNode, CodeRelationship, RelationType


@dataclass
class ParsedFile:
    """Result of parsing a single file."""
    path: str
    language: str
    checksum: str
    nodes: list[CodeNode]
    relationships: list[CodeRelationship]


class CodeParser:
    """Multi-language code parser using tree-sitter."""
    
    def __init__(self):
        if not HAS_TREE_SITTER:
            raise ImportError(
                "tree-sitter packages required. Install with:\n"
                "pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript"
            )
        
        self.parsers: dict[str, Parser] = {}
        self._init_parsers()
    
    def _init_parsers(self) -> None:
        """Initialize parsers for supported languages."""
        # Python
        python_lang = Language(tree_sitter_python.language())
        python_parser = Parser(python_lang)
        self.parsers["python"] = python_parser
        
        # JavaScript
        js_lang = Language(tree_sitter_javascript.language())
        js_parser = Parser(js_lang)
        self.parsers["javascript"] = js_parser
        
        # TypeScript
        ts_lang = Language(tree_sitter_typescript.language_typescript())
        ts_parser = Parser(ts_lang)
        self.parsers["typescript"] = ts_parser
    
    def parse_file(self, path: Path, language: str | None = None) -> ParsedFile | None:
        """Parse a source file and extract nodes and relationships."""
        if not path.exists() or not path.is_file():
            return None
        
        # Detect language from extension if not provided
        if language is None:
            language = self._detect_language(path)
        
        if language not in self.parsers:
            return None
        
        # Read file content
        try:
            content = path.read_bytes()
            text = content.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        
        # Calculate checksum
        checksum = hashlib.sha256(content).hexdigest()
        
        # Parse with tree-sitter
        parser = self.parsers[language]
        tree = parser.parse(content)
        
        # Extract nodes and relationships
        nodes: list[CodeNode] = []
        relationships: list[CodeRelationship] = []
        
        if language == "python":
            self._parse_python(tree.root_node, text, path.as_posix(), nodes, relationships)
        elif language == "javascript":
            self._parse_javascript(tree.root_node, text, path.as_posix(), nodes, relationships)
        elif language == "typescript":
            self._parse_typescript(tree.root_node, text, path.as_posix(), nodes, relationships)
        
        return ParsedFile(
            path=path.as_posix(),
            language=language,
            checksum=checksum,
            nodes=nodes,
            relationships=relationships,
        )
    
    def _detect_language(self, path: Path) -> str | None:
        """Detect language from file extension."""
        suffix = path.suffix.lower()
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
        }
        return mapping.get(suffix)
    
    def _parse_python(
        self,
        node: TSNode,
        text: str,
        path: str,
        nodes: list[CodeNode],
        relationships: list[CodeRelationship],
    ) -> None:
        """Parse Python code."""
        self._visit_python_node(node, text, path, nodes, relationships, parent_id=None)
    
    def _visit_python_node(
        self,
        node: TSNode,
        text: str,
        path: str,
        nodes: list[CodeNode],
        relationships: list[CodeRelationship],
        parent_id: str | None,
    ) -> None:
        """Visit Python AST node recursively."""
        node_type = node.type
        
        # Function definition
        if node_type == "function_definition":
            func_node = self._extract_python_function(node, text, path)
            if func_node:
                nodes.append(func_node)
                if parent_id:
                    relationships.append(CodeRelationship(
                        from_id=parent_id,
                        to_id=func_node.id,
                        rel_type=RelationType.CONTAINS,
                    ))
                parent_id = func_node.id
        
        # Class definition
        elif node_type == "class_definition":
            class_node = self._extract_python_class(node, text, path)
            if class_node:
                nodes.append(class_node)
                if parent_id:
                    relationships.append(CodeRelationship(
                        from_id=parent_id,
                        to_id=class_node.id,
                        rel_type=RelationType.CONTAINS,
                    ))
                parent_id = class_node.id
        
        # Recurse into children
        for child in node.children:
            self._visit_python_node(child, text, path, nodes, relationships, parent_id)
    
    def _extract_python_function(self, node: TSNode, text: str, path: str) -> FunctionNode | None:
        """Extract function information from Python AST node."""
        # Find function name
        name_node = node.child_by_field_name("name")
        if not name_node:
            return None
        
        name = text[name_node.start_byte:name_node.end_byte]
        
        # Extract parameters
        parameters: list[str] = []
        params_node = node.child_by_field_name("parameters")
        if params_node:
            for child in params_node.children:
                if child.type == "identifier":
                    param_name = text[child.start_byte:child.end_byte]
                    if param_name not in ("self", "cls"):
                        parameters.append(param_name)
        
        # Extract docstring
        docstring = None
        body_node = node.child_by_field_name("body")
        if body_node and body_node.child_count > 0:
            first_stmt = body_node.children[0]
            if first_stmt.type == "expression_statement":
                expr = first_stmt.children[0]
                if expr.type == "string":
                    docstring = text[expr.start_byte:expr.end_byte].strip("\"'")
        
        # Check if public (not starting with _)
        is_public = not name.startswith("_")
        
        # Create function ID
        func_id = f"{path}::{name}:{node.start_point[0]}"
        
        return FunctionNode(
            id=func_id,
            name=name,
            path=path,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            language="python",
            parameters=parameters,
            docstring=docstring,
            is_public=is_public,
        )
    
    def _extract_python_class(self, node: TSNode, text: str, path: str) -> ClassNode | None:
        """Extract class information from Python AST node."""
        # Find class name
        name_node = node.child_by_field_name("name")
        if not name_node:
            return None
        
        name = text[name_node.start_byte:name_node.end_byte]
        
        # Extract docstring
        docstring = None
        body_node = node.child_by_field_name("body")
        if body_node and body_node.child_count > 0:
            first_stmt = body_node.children[0]
            if first_stmt.type == "expression_statement":
                expr = first_stmt.children[0]
                if expr.type == "string":
                    docstring = text[expr.start_byte:expr.end_byte].strip("\"'")
        
        # Count methods
        methods_count = 0
        if body_node:
            for child in body_node.children:
                if child.type == "function_definition":
                    methods_count += 1
        
        # Create class ID
        class_id = f"{path}::{name}:{node.start_point[0]}"
        
        return ClassNode(
            id=class_id,
            name=name,
            path=path,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            language="python",
            docstring=docstring,
            methods_count=methods_count,
        )
    
    def _parse_javascript(
        self,
        node: TSNode,
        text: str,
        path: str,
        nodes: list[CodeNode],
        relationships: list[CodeRelationship],
    ) -> None:
        """Parse JavaScript code."""
        # Similar implementation for JavaScript
        pass
    
    def _parse_typescript(
        self,
        node: TSNode,
        text: str,
        path: str,
        nodes: list[CodeNode],
        relationships: list[CodeRelationship],
    ) -> None:
        """Parse TypeScript code."""
        # Similar implementation for TypeScript
        pass
