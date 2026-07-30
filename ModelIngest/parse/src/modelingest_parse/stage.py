"""Parse 阶段实现：文档解析为 Markdown。

支持多种文档格式，使用注册表模式管理解析器。
"""

from __future__ import annotations

from pathlib import Path

from modelingest_core import StageInput, StageOutput, PipelineStage, StageError
from modelingest_common import (
    Manifest,
    sha256_file,
    FrontmatterManager,
    ProgressTracker,
    ProgressStage,
)

from .registry import convert_to_markdown, list_parsers
from . import parsers  # 导入以注册内置解析器


class ParseStage(PipelineStage):
    """文档解析阶段。
    
    将各种格式的文档转换为 Markdown 格式。
    """
    
    @property
    def name(self) -> str:
        return "parse"
    
    @property
    def dependencies(self) -> list[str]:
        return ["markitdown"]  # 最小依赖
    
    def validate_input(self, input_data: StageInput) -> bool:
        """验证输入。
        
        支持单个文件或目录。
        """
        source = input_data.source_path
        return source.exists()
    
    def run(self, input_data: StageInput) -> StageOutput:
        """执行解析。
        
        配置参数：
        - parsers: 指定解析器优先级列表（默认使用全部）
        - extensions: 要处理的文件扩展名列表
        - overwrite: 是否覆盖已存在的文件
        """
        source = input_data.source_path
        config = input_data.config
        
        # 读取配置
        parser_priority = config.get("parsers", None)
        extensions = set(config.get("extensions", [
            ".pdf", ".docx", ".xlsx", ".pptx",
            ".html", ".htm", ".png", ".jpg", ".jpeg",
            ".md", ".txt",
        ]))
        overwrite = config.get("overwrite", False)
        
        # 确定输出目录
        output_root = Path(config.get("output_root", "./output"))
        output_root.mkdir(parents=True, exist_ok=True)
        
        # Manifest 路径
        manifest_path = output_root / ".ingest_cache" / "manifest.sqlite"
        
        stats = {"files": 0, "converted": 0, "skipped": 0, "errors": 0}
        errors = []
        
        # 收集待处理文件
        if source.is_file():
            files = [source]
        else:
            files = [
                f for f in source.rglob("*")
                if f.is_file() and f.suffix.lower() in extensions
            ]
        
        stats["files"] = len(files)
        
        with Manifest(manifest_path) as manifest:
            with ProgressTracker() as progress:
                for idx, file_path in enumerate(files):
                    progress.update(
                        ProgressStage.PARSE,
                        idx,
                        len(files),
                        f"解析 {file_path.name}"
                    )
                    
                    try:
                        self._process_file(
                            file_path,
                            source if source.is_dir() else source.parent,
                            output_root,
                            manifest,
                            parser_priority,
                            overwrite,
                            stats,
                            errors,
                        )
                    except Exception as e:
                        stats["errors"] += 1
                        errors.append(f"{file_path.name}: {e}")
                
                progress.update(
                    ProgressStage.PARSE,
                    len(files),
                    len(files),
                    f"完成 {stats['converted']} 个文件"
                )
        
        return StageOutput(
            output_path=output_root,
            metadata={
                "manifest_path": str(manifest_path),
                "parsers_available": list_parsers(),
            },
            stats=stats,
            errors=errors,
        )
    
    def _process_file(
        self,
        file_path: Path,
        source_root: Path,
        output_root: Path,
        manifest: Manifest,
        parser_priority: list[str] | None,
        overwrite: bool,
        stats: dict,
        errors: list,
    ):
        """处理单个文件。"""
        # 计算相对路径
        rel_path = str(file_path.relative_to(source_root))
        
        # 计算 SHA256
        file_hash = sha256_file(file_path)
        
        # 检查是否需要转换
        if not overwrite and not manifest.needs_convert(rel_path, file_hash):
            stats["skipped"] += 1
            return
        
        # 确定输出路径
        output_path = output_root / file_path.relative_to(source_root).with_suffix(".md")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 转换文档
        try:
            markdown, parser_name = convert_to_markdown(file_path, parser_priority)
        except Exception as e:
            stats["errors"] += 1
            errors.append(f"{file_path.name}: 转换失败 - {e}")
            return
        
        # 生成 frontmatter
        frontmatter = FrontmatterManager.build(
            source=rel_path,
            sha256=file_hash,
            converter=parser_name,
        )
        
        # 写入文件
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(frontmatter)
            f.write(markdown)
        
        # 更新 manifest
        manifest.record(
            rel_path=rel_path,
            sha256=file_hash,
            output_path=str(output_path.relative_to(output_root)),
            converter=parser_name,
        )
        
        stats["converted"] += 1
