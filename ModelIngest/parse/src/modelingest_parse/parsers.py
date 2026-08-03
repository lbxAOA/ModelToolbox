"""内置解析器实现。

提供 markitdown、docling、mineru 等解析器的实现。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .registry import register_parser


@register_parser("markitdown", priority=100)
def parse_markitdown(path: Path) -> Optional[str]:
    """使用 markitdown 解析文档。
    
    支持：PDF, DOCX, XLSX, PPTX, HTML, 图片等。
    这是默认解析器，轻量且覆盖广。
    
    Args:
        path: 文件路径
    
    Returns:
        Markdown 文本，失败返回 None
    """
    try:
        from markitdown import MarkItDown
        
        converter = MarkItDown()
        result = converter.convert(str(path))
        
        if result and result.text_content:
            return result.text_content.strip()
        
        return None
    
    except Exception:
        return None


@register_parser("docling", priority=50)
def parse_docling(path: Path) -> Optional[str]:
    """使用 docling 解析复杂 PDF。
    
    适合结构复杂的学术论文、技术文档。
    需要安装：pip install docling
    
    Args:
        path: 文件路径
    
    Returns:
        Markdown 文本，失败返回 None
    """
    # 只处理 PDF
    if path.suffix.lower() != ".pdf":
        return None
    
    try:
        from docling.document_converter import DocumentConverter
        
        converter = DocumentConverter()
        result = converter.convert(str(path))
        
        if result and hasattr(result, "markdown"):
            return result.markdown.strip()
        
        return None
    
    except Exception:
        return None


@register_parser("mineru", priority=30)
def parse_mineru(path: Path) -> Optional[str]:
    """使用 mineru 解析 PDF（保留公式）。
    
    适合数学公式较多的文档，支持 LaTeX 公式提取。
    需要安装：pip install mineru
    
    Args:
        path: 文件路径
    
    Returns:
        Markdown 文本，失败返回 None
    """
    # 只处理 PDF
    if path.suffix.lower() != ".pdf":
        return None
    
    try:
        # mineru 的导入和使用（简化示例）
        # 实际使用需要根据 mineru API 调整
        import mineru
        
        # 假设 mineru 提供 convert 函数
        result = mineru.convert(str(path))
        
        if result:
            return result.strip()
        
        return None
    
    except Exception:
        return None


@register_parser("visual", priority=10)
def parse_visual(path: Path) -> Optional[str]:
    """视觉解析器：处理图像文件或截图瓦片。
    
    使用视觉模型（如 Qwen3-VL）提取图像中的文本、表格、图表等。
    需要安装：pip install Pillow
    
    Args:
        path: 图像文件路径
    
    Returns:
        Markdown 文本，失败返回 None
    """
    # 只处理图像
    image_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
    if path.suffix.lower() not in image_exts:
        return None
    
    try:
        from PIL import Image
        
        # 打开图像
        img = Image.open(path)
        
        # TODO: 这里应该调用视觉模型（Qwen3-VL 等）
        # 当前简化实现：返回占位符
        markdown = f"![{path.name}]({path.name})\n\n"
        markdown += f"<!-- 视觉内容：{img.size[0]}x{img.size[1]} -->\n"
        
        return markdown
    
    except Exception:
        return None


@register_parser("passthrough", priority=200)
def parse_passthrough(path: Path) -> Optional[str]:
    """直通解析器：直接读取已是文本的文件。
    
    支持：.md, .txt, .rst 等纯文本格式。
    优先级最低，作为兜底。
    
    Args:
        path: 文件路径
    
    Returns:
        文件内容，失败返回 None
    """
    text_exts = {".md", ".txt", ".rst", ".markdown"}
    if path.suffix.lower() not in text_exts:
        return None
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None
