"""端到端知识库构建器 —— 从 URL/本地目录到结构化知识库的完整流程。

核心流程:
1. 内容获取 (crawl/scan)
2. 格式转换 (parse)
3. 清洗 (clean)
4. 蒸馏 (distill, 可选)
5. 组织 (organize)

使用方式:
    modelingest build --source <URL或本地路径> --output <知识库目录> [选项]
"""

from __future__ import annotations

import shutil
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

from .config import IngestConfig
from .crawler import CrawlConfig, crawl
from . import pipeline


class SourceType(Enum):
    """输入源类型"""
    WEB_URL = "web"
    LOCAL_DIR = "local"
    UNKNOWN = "unknown"


class BuildStage(Enum):
    """构建阶段"""
    INIT = "初始化"
    FETCH = "内容获取"
    PARSE = "格式转换"
    CLEAN = "内容清洗"
    DISTILL = "知识蒸馏"
    ORGANIZE = "知识库组织"
    COMPLETE = "完成"


@dataclass
class BuildProgress:
    """构建进度信息"""
    stage: BuildStage
    current: int = 0
    total: int = 0
    message: str = ""
    errors: list[str] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        """返回当前阶段进度百分比"""
        if self.total == 0:
            return 0.0
        return min(100.0, (self.current / self.total) * 100)


@dataclass
class BuildConfig:
    """知识库构建配置"""

    # 输入源
    source: str  # URL 或本地目录路径
    source_type: SourceType = SourceType.UNKNOWN

    # 输出路径
    output: Path = field(default_factory=lambda: Path("./knowledge_base"))

    # 领域配置
    domain: str = "通用"  # 算法/硬件/数学/通用

    # 质量配置
    quality: str = "medium"  # high(启用蒸馏) / medium / low
    enable_distill: bool = False

    # 输出结构
    structure: str = "obsidian"  # obsidian / flat

    # Web 爬取配置
    crawl_depth: int = 3
    crawl_max_pages: int = 500
    crawl_delay: float = 0.5
    same_domain_only: bool = True

    # 转换配置
    extract_pdf_pages: bool = True
    clean_html: bool = True
    quality_filter: bool = True

    # 蒸馏配置 (quality=high 时使用)
    distill_profile: str = "concept"
    distill_role: str = "teacher"

    # 临时目录
    temp_dir: Optional[Path] = None
    keep_temp: bool = False  # 是否保留临时文件

    # 进度回调
    progress_callback: Optional[Callable[[BuildProgress], None]] = None

    def __post_init__(self):
        """初始化后处理"""
        # 检测输入源类型
        if self.source_type == SourceType.UNKNOWN:
            self.source_type = self._detect_source_type()

        # 根据质量等级设置蒸馏和过滤
        if self.quality == "high":
            self.enable_distill = True
        elif self.quality == "low":
            # low 质量模式：禁用质量过滤（快速构建，保留所有内容）
            self.quality_filter = False

        # 设置临时目录
        if self.temp_dir is None:
            self.temp_dir = Path(tempfile.gettempdir()) / f"modeltoolbox-build-{uuid.uuid4().hex}"

    def _detect_source_type(self) -> SourceType:
        """自动检测输入源类型"""
        if self.source.startswith(("http://", "https://")):
            return SourceType.WEB_URL
        elif Path(self.source).exists():
            return SourceType.LOCAL_DIR
        return SourceType.UNKNOWN


@dataclass
class BuildResult:
    """构建结果"""
    success: bool
    output_path: Path
    stats: dict
    errors: list[str] = field(default_factory=list)
    duration: float = 0.0


class KnowledgeBaseBuilder:
    """知识库构建器"""

    def __init__(self, config: BuildConfig):
        self.config = config
        self.progress = BuildProgress(stage=BuildStage.INIT)

    def build(self) -> BuildResult:
        """执行完整构建流程"""
        start_time = time.time()
        stats = {
            "fetched": 0,
            "converted": 0,
            "filtered": 0,
            "distilled": 0,
            "organized": 0,
        }
        errors = []

        try:
            # 1. 初始化
            self._update_progress(BuildStage.INIT, 0, 1, "准备构建环境...")
            self._prepare_directories()
            self._update_progress(BuildStage.INIT, 1, 1, "构建环境就绪")

            # 2. 内容获取
            raw_dir = self._fetch_content()
            stats["fetched"] = self._count_files(raw_dir)

            # 3. 格式转换
            md_dir = self._parse_content(raw_dir)
            stats["converted"] = self._count_files(md_dir)

            # 4. 清洗 (已集成在 parse 中)

            # 5. 蒸馏 (可选)
            if self.config.enable_distill:
                distill_dir = self._distill_content(md_dir)
                stats["distilled"] = self._count_files(distill_dir)
            else:
                distill_dir = md_dir

            # 6. 组织
            final_dir = self._organize_content(distill_dir)
            stats["organized"] = self._count_files(final_dir)

            self._update_progress(BuildStage.COMPLETE, 1, 1, "知识库构建完成")

            # 7. 清理临时文件 (在完成后清理，除非用户要求保留)
            if not getattr(self.config, 'keep_temp', False):
                self._cleanup_temp()

            return BuildResult(
                success=True,
                output_path=self.config.output,
                stats=stats,
                errors=errors,
                duration=time.time() - start_time
            )

        except Exception as e:
            errors.append(str(e))
            return BuildResult(
                success=False,
                output_path=self.config.output,
                stats=stats,
                errors=errors,
                duration=time.time() - start_time
            )

    def _prepare_directories(self):
        """准备目录结构"""
        self.config.output.mkdir(parents=True, exist_ok=True)
        self.config.temp_dir.mkdir(parents=True, exist_ok=True)

    def _fetch_content(self) -> Path:
        """获取内容 (Web 爬取或本地扫描)"""
        raw_dir = self.config.temp_dir / "raw"
        raw_dir.mkdir(exist_ok=True)

        if self.config.source_type == SourceType.WEB_URL:
            self._update_progress(BuildStage.FETCH, 0, 0, f"开始爬取: {self.config.source}")

            # 使用现有 crawler
            crawl_cfg = CrawlConfig(
                urls=[self.config.source],
                output_root=raw_dir,
                manifest_path=raw_dir / ".crawl_manifest.sqlite",
                max_depth=self.config.crawl_depth,
                same_domain_only=self.config.same_domain_only,
                delay=self.config.crawl_delay,
                timeout=20.0,
                overwrite=False,
            )

            result = crawl(crawl_cfg)
            self._update_progress(
                BuildStage.FETCH,
                result.fetched,
                result.fetched + result.skipped,
                f"已获取 {result.fetched} 个文件"
            )

        elif self.config.source_type == SourceType.LOCAL_DIR:
            self._update_progress(BuildStage.FETCH, 0, 0, f"扫描本地目录: {self.config.source}")

            # 复制本地文件到临时目录
            source_path = Path(self.config.source).resolve()
            excluded_roots = {
                self.config.output.resolve(),
                self.config.temp_dir.resolve(),
            }
            file_count = 0
            for src_file in source_path.rglob("*"):
                resolved_file = src_file.resolve()
                if src_file.is_file() and not any(
                    resolved_file.is_relative_to(root) for root in excluded_roots
                ):
                    rel_path = src_file.relative_to(source_path)
                    dst_file = raw_dir / rel_path
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dst_file)
                    file_count += 1

            self._update_progress(BuildStage.FETCH, file_count, file_count, f"已扫描 {file_count} 个文件")
        else:
            raise ValueError(f"不支持的输入源: {self.config.source}")

        return raw_dir

    def _parse_content(self, raw_dir: Path) -> Path:
        """解析内容为 Markdown"""
        md_dir = self.config.temp_dir / "markdown"
        md_dir.mkdir(exist_ok=True)

        self._update_progress(BuildStage.PARSE, 0, 0, "开始格式转换...")

        # 使用现有 pipeline
        ingest_cfg = IngestConfig(
            source_root=raw_dir,
            output_root=md_dir,
            manifest_path=md_dir / ".ingest_manifest.sqlite",
            extract_pdf_pages=self.config.extract_pdf_pages,
            clean_html=self.config.clean_html,
            quality_filter=self.config.quality_filter,
            overwrite=False,
        )

        summary = pipeline.run(ingest_cfg)

        # 复制 raw 目录中已经是 .md 的文件到 markdown 目录
        # （pipeline 会跳过它们，但我们需要保留）
        for md_file in raw_dir.rglob("*.md"):
            rel_path = md_file.relative_to(raw_dir)
            dst_file = md_dir / rel_path
            if not dst_file.exists():
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(md_file, dst_file)

        self._update_progress(
            BuildStage.PARSE,
            summary.converted,
            summary.converted + summary.skipped,
            f"已转换 {summary.converted} 个文件"
        )

        return md_dir

    def _distill_content(self, md_dir: Path) -> Path:
        """蒸馏内容 (可选)"""
        distill_dir = self.config.temp_dir / "distilled"
        distill_dir.mkdir(exist_ok=True)

        self._update_progress(BuildStage.DISTILL, 0, 0, "开始知识蒸馏...")

        # TODO: 调用现有 distill 模块
        # 这里需要根据实际 distill 模块的接口来实现

        self._update_progress(BuildStage.DISTILL, 1, 1, "知识蒸馏完成")

        return distill_dir

    def _organize_content(self, content_dir: Path) -> Path:
        """组织知识库结构"""
        final_dir = self.config.output

        self._update_progress(BuildStage.ORGANIZE, 0, 0, "开始组织知识库...")

        # 先复制所有 markdown 文件到输出目录
        if content_dir != final_dir:
            for md_file in content_dir.rglob("*.md"):
                rel_path = md_file.relative_to(content_dir)
                dst_file = final_dir / rel_path
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(md_file, dst_file)

        # 使用 organizer 模块组织结构
        from .organizer import OrganizeConfig, organize_knowledge_base

        organize_cfg = OrganizeConfig(
            source_dir=final_dir,  # 现在从 final_dir 读取
            output_dir=final_dir,  # 输出到同一目录
            structure=self.config.structure,
            domain=self.config.domain,
            create_index=True,
            create_moc=True,
            auto_categorize=True,
        )

        stats = organize_knowledge_base(organize_cfg)

        # 生成知识库元数据
        self._generate_metadata(final_dir)

        self._update_progress(
            BuildStage.ORGANIZE,
            stats.get("total_notes", 0),
            stats.get("total_notes", 0),
            f"已组织 {stats.get('total_notes', 0)} 个笔记"
        )

        return final_dir

    def _generate_metadata(self, kb_dir: Path):
        """生成知识库元数据"""
        metadata = {
            "name": kb_dir.name,
            "domain": self.config.domain,
            "source": self.config.source,
            "created_at": datetime.now().isoformat(),
            "structure": self.config.structure,
            "quality": self.config.quality,
        }

        meta_dir = kb_dir / ".kb_meta"
        meta_dir.mkdir(exist_ok=True)

        import json
        (meta_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def _cleanup_temp(self):
        """清理临时文件"""
        if self.config.temp_dir and self.config.temp_dir.exists():
            shutil.rmtree(self.config.temp_dir, ignore_errors=True)

    def _count_files(self, directory: Path) -> int:
        """统计目录中的文件数"""
        if not directory.exists():
            return 0
        return sum(1 for _ in directory.rglob("*") if _.is_file())

    def _update_progress(self, stage: BuildStage, current: int, total: int, message: str):
        """更新进度"""
        self.progress.stage = stage
        self.progress.current = current
        self.progress.total = total
        self.progress.message = message

        if self.config.progress_callback:
            self.config.progress_callback(self.progress)
