"""ModelIngest 核心流程：遍历源目录 → 转换 → 写出带 front-matter 的 md（增量）。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .assets import extract_pdf_pages
from .config import IMAGE_EXTS, IngestConfig
from .converter import ConversionError, convert_to_markdown
from .frontmatter import build_frontmatter
from .manifest import Manifest, sha256_file


@dataclass
class FileResult:
    rel_path: str
    status: str  # "converted" | "skipped" | "failed"
    output_path: str | None = None
    error: str | None = None


@dataclass
class RunSummary:
    converted: int = 0
    skipped: int = 0
    failed: int = 0
    results: list[FileResult] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.results is None:
            self.results = []


def _iter_source_files(cfg: IngestConfig):
    for path in sorted(cfg.source_root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in cfg.exts:
            continue
        # 跳过 markdown 自身（已经是目标格式）与隐藏目录
        if any(part.startswith(".") for part in path.relative_to(cfg.source_root).parts):
            continue
        yield path


def run(cfg: IngestConfig) -> RunSummary:
    """执行一次转换。"""
    cfg.output_root.mkdir(parents=True, exist_ok=True)
    manifest = Manifest(cfg.manifest_path)
    summary = RunSummary()

    try:
        for src in _iter_source_files(cfg):
            rel = src.relative_to(cfg.source_root).as_posix()
            digest = sha256_file(src)

            if not cfg.overwrite and not manifest.needs_convert(rel, digest):
                summary.skipped += 1
                summary.results.append(FileResult(rel, "skipped"))
                continue

            out_path = (cfg.output_root / src.relative_to(cfg.source_root)).with_suffix(".md")
            out_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                body, converter_name = convert_to_markdown(src)
            except ConversionError as exc:
                summary.failed += 1
                summary.results.append(FileResult(rel, "failed", error=str(exc)))
                continue

            # PDF 抽页图（多模态素材，本地保留）
            assets: list[str] = []
            if cfg.extract_pdf_pages and src.suffix.lower() == ".pdf":
                assets_dir = out_path.parent / "assets" / out_path.stem
                names = extract_pdf_pages(src, assets_dir, dpi=cfg.pdf_page_dpi)
                assets = [f"assets/{out_path.stem}/{n}" for n in names]
            elif src.suffix.lower() in IMAGE_EXTS:
                # 图片本身即 asset：记录其源相对路径以便训练引用
                assets = [rel]

            fm = build_frontmatter(
                source=rel,
                sha256=digest,
                converter=converter_name,
                assets=assets,
            )
            out_path.write_text(fm + body, encoding="utf-8")

            manifest.record(rel, digest, out_path.relative_to(cfg.output_root).as_posix(), converter_name)
            summary.converted += 1
            summary.results.append(FileResult(rel, "converted", output_path=str(out_path)))
    finally:
        manifest.close()

    return summary


def status(cfg: IngestConfig) -> dict:
    """对比源目录与 manifest，报告 待转/已转/已失效(源被删) 数量。"""
    manifest = Manifest(cfg.manifest_path)
    try:
        recorded = {r[0]: r[1] for r in manifest.all_records()}
        present, pending, changed = set(), 0, 0
        for src in _iter_source_files(cfg):
            rel = src.relative_to(cfg.source_root).as_posix()
            present.add(rel)
            digest = sha256_file(src)
            if rel not in recorded:
                pending += 1
            elif recorded[rel] != digest:
                changed += 1
        stale = [rel for rel in recorded if rel not in present]
        return {
            "recorded": len(recorded),
            "pending_new": pending,
            "pending_changed": changed,
            "stale_source_deleted": len(stale),
            "stale_list": stale,
        }
    finally:
        manifest.close()


def clean(cfg: IngestConfig) -> int:
    """删除 manifest 中源文件已不存在的记录及其输出 md。返回清理数量。"""
    manifest = Manifest(cfg.manifest_path)
    removed = 0
    try:
        for rel, _sha, out_rel, _conv, _ts in manifest.all_records():
            if not (cfg.source_root / rel).exists():
                out_file = cfg.output_root / out_rel
                if out_file.exists():
                    out_file.unlink()
                manifest.remove(rel)
                removed += 1
    finally:
        manifest.close()
    return removed
