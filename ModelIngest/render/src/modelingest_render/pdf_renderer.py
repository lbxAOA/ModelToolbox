"""PDF 渲染器：将 PDF 页面转换为图像。

使用 PyMuPDF (fitz) 渲染 PDF 页面为高清图像。
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

try:
    import fitz  # PyMuPDF
    from PIL import Image
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class PDFRenderer:
    """PDF 页面渲染器。
    
    使用 PyMuPDF 将 PDF 页面渲染为图像。
    """
    
    def __init__(self, dpi: int = 200):
        """初始化 PDF 渲染器。
        
        Args:
            dpi: 渲染 DPI（默认 200，越高越清晰但文件越大）
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError(
                "需要安装 PyMuPDF 和 Pillow：\n"
                "  pip install PyMuPDF Pillow"
            )
        
        self.dpi = dpi
        self.zoom = dpi / 72  # PDF 默认 72 DPI
    
    def render_pages(
        self,
        pdf_path: Path,
        output_dir: Path,
        img_format: Literal["png", "jpg", "webp"] = "png",
        page_range: tuple[int, int] | None = None,
    ) -> list[Path]:
        """渲染 PDF 所有页面为图像。
        
        Args:
            pdf_path: PDF 文件路径
            output_dir: 输出目录
            img_format: 图像格式
            page_range: 页面范围 (start, end)，None 表示全部页面
        
        Returns:
            生成的图像文件路径列表
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        doc = fitz.open(pdf_path)
        pages = []
        
        try:
            start_page = page_range[0] if page_range else 0
            end_page = page_range[1] if page_range else doc.page_count
            
            for page_num in range(start_page, end_page):
                page = doc[page_num]
                
                # 渲染为 pixmap
                mat = fitz.Matrix(self.zoom, self.zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # 保存为图像
                page_filename = f"{pdf_path.stem}_p{page_num + 1:04d}.{img_format}"
                page_path = output_dir / page_filename
                
                # PyMuPDF 直接保存
                if img_format.lower() == "png":
                    pix.save(page_path)
                else:
                    # 其他格式通过 PIL 转换
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img.save(page_path, format=img_format.upper())
                
                pages.append(page_path)
        
        finally:
            doc.close()
        
        return pages
    
    def render_page(
        self,
        pdf_path: Path,
        page_num: int,
        output_path: Path,
        img_format: Literal["png", "jpg", "webp"] = "png",
    ) -> Path:
        """渲染 PDF 单个页面。
        
        Args:
            pdf_path: PDF 文件路径
            page_num: 页码（从 0 开始）
            output_path: 输出文件路径
            img_format: 图像格式
        
        Returns:
            输出文件路径
        """
        doc = fitz.open(pdf_path)
        
        try:
            page = doc[page_num]
            mat = fitz.Matrix(self.zoom, self.zoom)
            pix = page.get_pixmap(matrix=mat)
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if img_format.lower() == "png":
                pix.save(output_path)
            else:
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.save(output_path, format=img_format.upper())
            
            return output_path
        
        finally:
            doc.close()
    
    def get_page_count(self, pdf_path: Path) -> int:
        """获取 PDF 页数。
        
        Args:
            pdf_path: PDF 文件路径
        
        Returns:
            页数
        """
        doc = fitz.open(pdf_path)
        try:
            return doc.page_count
        finally:
            doc.close()
