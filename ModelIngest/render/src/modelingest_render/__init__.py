"""ModelIngest Render：视觉渲染阶段。

使用 Playwright 渲染网页/PDF 为截图瓦片，保留视觉信息。
这是 ModelIngest v2.0 的核心创新，解决传统文本解析丢失表格/图表的问题。
"""

__version__ = "2.0.0"

from .stage import RenderStage

__all__ = ["RenderStage"]
