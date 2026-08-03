"""ModelIngest Parse：文档解析阶段。

将各种格式文档（PDF/DOCX/HTML/图片等）转换为 Markdown。
支持多解析器注册和优先级降级。
"""

__version__ = "2.0.0"

from .stage import ParseStage
from .registry import register_parser, convert_to_markdown, list_parsers

__all__ = [
    "ParseStage",
    "register_parser",
    "convert_to_markdown",
    "list_parsers",
]
