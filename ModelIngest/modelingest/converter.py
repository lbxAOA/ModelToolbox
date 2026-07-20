"""转换分发（兼容层）。

历史上本模块直接调用 markitdown。现已抽出可插拔解析器注册表到 :mod:`parsers`
（mineru / docling / marker / markitdown / passthrough，逐级降级）。
此文件保留原有导入路径 ``from .converter import convert_to_markdown, ConversionError``，
委托给注册表实现，向后兼容。
"""

from __future__ import annotations

from .parsers import ConversionError, convert_to_markdown

__all__ = ["ConversionError", "convert_to_markdown"]
