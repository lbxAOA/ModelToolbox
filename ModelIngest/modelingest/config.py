"""ModelIngest 配置。

约定：
- 原始文档留在源目录（``source_root``），不移动、不上传。
- 转换产物 ``*.md`` 写入 ``output_root``，镜像源目录结构。
- PDF 抽取的页图 / 图表写入 ``output_root/<相对路径>/assets``（被 .gitignore 排除）。
- 增量状态存于 ``manifest_path``（sqlite）。
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# 支持的源文件扩展名（小写，含点）。
SUPPORTED_EXTS: set[str] = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
    ".txt",
    ".html",
    ".htm",
    ".csv",
    ".json",
    ".epub",
}

# 图片类扩展名（转换时可选 OCR / 视觉描述，且本身作为 asset 保留）。
IMAGE_EXTS: set[str] = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}


@dataclass
class IngestConfig:
    """一次转换运行的配置。"""

    source_root: Path
    output_root: Path
    manifest_path: Path = field(default=Path(".ingest_cache/ingest_manifest.sqlite"))
    extract_pdf_pages: bool = True
    pdf_page_dpi: int = 150
    overwrite: bool = False  # True 时忽略 manifest，全量重转
    exts: set[str] = field(default_factory=lambda: set(SUPPORTED_EXTS))
    # 清洗（阶段 A）开关：见 cleaner.py。
    clean_html: bool = True            # 网页正文去噪（剔除 nav/广告/隐藏样板）
    neutralize_injection: bool = True  # 中和疑似面向 AI 的注入指令
    quality_filter: bool = True        # 过滤空内容/登录墙/错误页等低质量源
    near_dup_check: bool = True        # 跨来源近似去重（SimHash）
    near_dup_max_distance: int = 3     # SimHash 汉明距离阈值（64 bit）

    def __post_init__(self) -> None:
        self.source_root = Path(self.source_root).resolve()
        self.output_root = Path(self.output_root).resolve()
        self.manifest_path = Path(self.manifest_path)
        if not self.manifest_path.is_absolute():
            self.manifest_path = (self.output_root / self.manifest_path).resolve()

    @classmethod
    def from_env(cls, source_root: str | os.PathLike, output_root: str | os.PathLike) -> "IngestConfig":
        def _bool_env(name: str, default: str = "1") -> bool:
            return os.getenv(name, default) not in {"0", "false", "False"}

        return cls(
            source_root=Path(source_root),
            output_root=Path(output_root),
            extract_pdf_pages=_bool_env("INGEST_EXTRACT_PDF_PAGES"),
            pdf_page_dpi=int(os.getenv("INGEST_PDF_DPI", "150")),
            clean_html=_bool_env("INGEST_CLEAN_HTML"),
            neutralize_injection=_bool_env("INGEST_NEUTRALIZE_INJECTION"),
            quality_filter=_bool_env("INGEST_QUALITY_FILTER"),
            near_dup_check=_bool_env("INGEST_NEAR_DUP_CHECK"),
            near_dup_max_distance=int(os.getenv("INGEST_NEAR_DUP_DISTANCE", "3")),
        )
