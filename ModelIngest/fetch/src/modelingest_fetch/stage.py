"""Fetch 阶段实现：内容获取（网页爬取或本地扫描）。

根据输入类型（URL 或本地路径），执行网页爬取或文件扫描。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .crawler import CrawlConfig, DiscoverConfig, crawl, discover


class FetchStage:
    """内容获取阶段。
    
    支持：
    - 网页爬取（URL）
    - 本地文件扫描（目录/文件）
    """
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
    
    def discover(
        self,
        urls: list[str],
        max_depth: int = 1,
        same_domain_only: bool = True,
        max_pages: int = 100,
    ):
        """发现链接（不下载）。"""
        cfg = DiscoverConfig(
            urls=urls,
            max_depth=max_depth,
            same_domain_only=same_domain_only,
            max_pages=max_pages,
            delay=self.config.get("delay", 0.5),
            timeout=self.config.get("timeout", 20.0),
            user_agent=self.config.get("user_agent"),
            respect_robots=self.config.get("respect_robots", True),
        )
        return discover(cfg)
    
    def crawl(
        self,
        urls: list[str],
        output_root: Path,
        max_depth: int = 0,
        same_domain_only: bool = True,
        overwrite: bool = False,
    ):
        """执行网页爬取。"""
        manifest_path = output_root / ".crawl_cache" / "manifest.sqlite"
        
        cfg = CrawlConfig(
            urls=urls,
            output_root=output_root,
            manifest_path=manifest_path,
            max_depth=max_depth,
            same_domain_only=same_domain_only,
            overwrite=overwrite,
            delay=self.config.get("delay", 1.0),
            timeout=self.config.get("timeout", 20.0),
            user_agent=self.config.get("user_agent"),
            respect_robots=self.config.get("respect_robots", True),
            max_pages=self.config.get("max_pages", 200),
        )
        return crawl(cfg)
    
    def scan_local(self, source_path: Path) -> list[Path]:
        """扫描本地目录，返回所有支持的文件。"""
        if source_path.is_file():
            return [source_path]
        
        supported_exts = {
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            ".html", ".htm", ".txt", ".md", ".csv", ".json",
            ".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp",
        }
        
        files = []
        for ext in supported_exts:
            files.extend(source_path.rglob(f"*{ext}"))
        
        return sorted(files)
            errors.append("网页爬取功能待实现（可复用现有 crawler.py）")
            
            return StageOutput(
                output_path=output_dir,
                metadata={"source_type": "web"},
                stats=stats,
                errors=errors,
            )
        
        else:
            # 本地文件/目录，直接返回
            local_path = Path(source)
            
            if local_path.is_file():
                stats["files"] = 1
            elif local_path.is_dir():
                stats["files"] = len(list(local_path.rglob("*")))
            
            return StageOutput(
                output_path=local_path,
                metadata={"source_type": "local"},
                stats=stats,
                errors=errors,
            )
