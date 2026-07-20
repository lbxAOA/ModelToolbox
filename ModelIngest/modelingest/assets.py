"""PDF 页图 / 图表抽取。

用于多模态训练：把 PDF 每页渲染成图片（或抽取内嵌图），存到输出目录的 ``assets`` 下。
这些图本地保留、被 .gitignore 排除，不随仓库上传。

依赖 PyMuPDF(fitz)，若未安装则优雅降级（返回空列表）。
"""

from __future__ import annotations

from pathlib import Path


def extract_pdf_pages(pdf_path: Path, assets_dir: Path, dpi: int = 150) -> list[str]:
    """把 PDF 每页渲染为 PNG，返回相对 assets_dir 的文件名列表。

    未安装 PyMuPDF 时返回空列表（不报错），转换仍可继续，只是没有页图。
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return []

    assets_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    with fitz.open(str(pdf_path)) as doc:
        stem = pdf_path.stem
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=matrix)
            name = f"{stem}_p{i + 1:04d}.png"
            pix.save(str(assets_dir / name))
            written.append(name)
    return written
