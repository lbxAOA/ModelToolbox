"""Render 阶段实现：将网页/PDF 渲染为截图瓦片。

这是 ModelIngest v2.0 的核心创新，保留文档的视觉信息（表格、图表、布局）。
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from modelingest_core import StageInput, StageOutput, PipelineStage, StageError
from modelingest_common import ProgressTracker, ProgressStage

from .screenshot import WebScreenshotter
from .tile_generator import TileGenerator
from .pdf_renderer import PDFRenderer


class RenderStage(PipelineStage):
    """视觉渲染阶段。
    
    将输入的网页或 PDF 渲染为截图瓦片（tiles），保留视觉信息。
    """
    
    @property
    def name(self) -> str:
        return "render"
    
    @property
    def dependencies(self) -> list[str]:
        return ["playwright", "PIL"]
    
    def validate_input(self, input_data: StageInput) -> bool:
        """验证输入。
        
        支持的输入：
        - HTML 文件
        - URL（需要以 http:// 或 https:// 开头）
        - PDF 文件（需要安装 PyMuPDF）
        """
        source = input_data.source_path
        
        # URL
        if str(source).startswith(("http://", "https://")):
            return True
        
        # 本地文件
        if not source.exists():
            return False
        
        # 支持的文件类型
        suffix = source.suffix.lower()
        return suffix in [".html", ".htm", ".pdf"]
    
    def run(self, input_data: StageInput) -> StageOutput:
        """执行渲染。
        
        配置参数（从 input_data.config 读取）：
        - mode: 'tiles' | 'full' | 'off'（默认 'tiles'）
        - tile_width: 瓦片宽度（默认 1024）
        - tile_height: 瓦片高度（默认 1024）
        - overlap: 瓦片重叠像素（默认 100）
        - dpi: PDF 渲染 DPI（默认 200）
        - format: 图片格式（默认 'png'）
        """
        source = input_data.source_path
        config = input_data.config
        
        # 读取配置
        mode: Literal["tiles", "full", "off"] = config.get("mode", "tiles")
        tile_width = config.get("tile_width", 1024)
        tile_height = config.get("tile_height", 1024)
        overlap = config.get("overlap", 100)
        dpi = config.get("dpi", 200)
        img_format = config.get("format", "png")
        
        # 确定输出目录
        output_dir = Path(config.get("output_root", "./output")) / ".ingest_cache" / "tiles"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        stats = {"files": 0, "tiles": 0, "errors": 0}
        errors = []
        
        try:
            with ProgressTracker() as progress:
                progress.update(ProgressStage.RENDER, 0, 1, f"渲染 {source.name}")
                
                # 根据输入类型选择渲染器
                if str(source).startswith(("http://", "https://")):
                    # 网页渲染
                    tiles = self._render_webpage(
                        str(source),
                        output_dir,
                        mode,
                        tile_width,
                        tile_height,
                        overlap,
                        img_format,
                    )
                elif source.suffix.lower() == ".pdf":
                    # PDF 渲染
                    tiles = self._render_pdf(
                        source,
                        output_dir,
                        mode,
                        tile_width,
                        tile_height,
                        overlap,
                        dpi,
                        img_format,
                    )
                else:
                    # HTML 文件渲染
                    tiles = self._render_html_file(
                        source,
                        output_dir,
                        mode,
                        tile_width,
                        tile_height,
                        overlap,
                        img_format,
                    )
                
                stats["files"] = 1
                stats["tiles"] = len(tiles)
                
                progress.update(ProgressStage.RENDER, 1, 1, f"生成 {len(tiles)} 个瓦片")
        
        except Exception as e:
            stats["errors"] = 1
            errors.append(f"渲染失败: {e}")
            raise StageError(self.name, f"渲染失败: {e}") from e
        
        return StageOutput(
            output_path=output_dir,
            metadata={
                "tiles": [str(t) for t in tiles],
                "source_type": "web" if str(source).startswith("http") else "local",
            },
            stats=stats,
            errors=errors,
        )
    
    def _render_webpage(
        self,
        url: str,
        output_dir: Path,
        mode: str,
        tile_width: int,
        tile_height: int,
        overlap: int,
        img_format: str,
    ) -> list[Path]:
        """渲染网页为截图。"""
        screenshotter = WebScreenshotter()
        
        if mode == "full":
            # 全页截图
            screenshot = screenshotter.capture_full_page(url)
            output_file = output_dir / f"page_full.{img_format}"
            screenshot.save(output_file, format=img_format.upper())
            return [output_file]
        
        elif mode == "tiles":
            # 瓦片截图
            screenshot = screenshotter.capture_full_page(url)
            tile_gen = TileGenerator(tile_width, tile_height, overlap)
            tiles = tile_gen.generate_tiles(screenshot, output_dir, img_format)
            return tiles
        
        else:
            return []
    
    def _render_html_file(
        self,
        html_path: Path,
        output_dir: Path,
        mode: str,
        tile_width: int,
        tile_height: int,
        overlap: int,
        img_format: str,
    ) -> list[Path]:
        """渲染 HTML 文件为截图。"""
        file_url = html_path.as_uri()
        return self._render_webpage(
            file_url,
            output_dir,
            mode,
            tile_width,
            tile_height,
            overlap,
            img_format,
        )
    
    def _render_pdf(
        self,
        pdf_path: Path,
        output_dir: Path,
        mode: str,
        tile_width: int,
        tile_height: int,
        overlap: int,
        dpi: int,
        img_format: str,
    ) -> list[Path]:
        """渲染 PDF 为截图。"""
        renderer = PDFRenderer(dpi)
        
        if mode == "full":
            # 每页一张完整图
            return renderer.render_pages(pdf_path, output_dir, img_format)
        
        elif mode == "tiles":
            # 每页分割为瓦片
            pages = renderer.render_pages(pdf_path, output_dir, img_format)
            
            # 对每页生成瓦片
            tile_gen = TileGenerator(tile_width, tile_height, overlap)
            all_tiles = []
            
            for page_img in pages:
                from PIL import Image
                img = Image.open(page_img)
                tiles = tile_gen.generate_tiles(
                    img,
                    output_dir,
                    img_format,
                    prefix=page_img.stem,
                )
                all_tiles.extend(tiles)
            
            return all_tiles
        
        else:
            return []
