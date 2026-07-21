"""ModelIngest 核心流程：遍历源目录 → 清洗 → 转换 → 写出带 front-matter 的 md（增量）。"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from . import cleaner
from .assets import extract_pdf_pages
from .config import IMAGE_EXTS, IngestConfig
from .converter import ConversionError, convert_to_markdown
from .frontmatter import build_frontmatter
from .manifest import Manifest, sha256_file

_HTML_EXTS = {".html", ".htm"}


@dataclass
class FileResult:
    rel_path: str
    status: str  # "converted" | "skipped" | "filtered" | "failed"
    output_path: str | None = None
    error: str | None = None
    note: str | None = None  # 附加信息（如近似去重命中），不代表失败


@dataclass
class RunSummary:
    converted: int = 0
    skipped: int = 0
    filtered: int = 0
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
        rel_parts = path.relative_to(cfg.source_root).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        if cfg.include is not None:
            rel = path.relative_to(cfg.source_root).as_posix()
            if rel not in cfg.include:
                continue
        yield path


def _prepare_source_for_conversion(src: Path, cfg: IngestConfig) -> tuple[Path, bool]:
    """网页源文件在转换前先去噪；返回 (实际用于转换的路径, 是否为需清理的临时文件)。"""
    if not cfg.clean_html or src.suffix.lower() not in _HTML_EXTS:
        return src, False
    try:
        raw = src.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return src, False
    cleaned = cleaner.strip_html_boilerplate(raw)
    fd, tmp_name = tempfile.mkstemp(suffix=src.suffix)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(cleaned)
    except Exception:
        Path(tmp_name).unlink(missing_ok=True)
        return src, False
    return Path(tmp_name), True


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

            conv_src, is_tmp = _prepare_source_for_conversion(src, cfg)
            try:
                body, converter_name = convert_to_markdown(conv_src)
            except ConversionError as exc:
                summary.failed += 1
                summary.results.append(FileResult(rel, "failed", error=str(exc)))
                continue
            finally:
                if is_tmp:
                    conv_src.unlink(missing_ok=True)

            # 文本规范化：编码/换行/零宽字符清理（无条件执行）。
            body = cleaner.normalize_text(body)

            # Prompt injection 中和：隔离"疑似面向 AI 的隐藏指令"，不删除原文。
            injection_flags: list[str] = []
            if cfg.neutralize_injection:
                body, injection_flags = cleaner.neutralize_prompt_injection(body)

            # 质量过滤：空内容/登录墙/错误页等噪声源不产出 md，但仍记入 manifest
            # （避免每次重跑都重新转换 + 重新判定）。
            if cfg.quality_filter:
                issue = cleaner.quality_issue(body)
                if issue:
                    manifest.record(rel, digest, "", f"filtered:{issue}")
                    summary.filtered += 1
                    summary.results.append(FileResult(rel, "filtered", error=issue))
                    continue

            # 近似去重：跨来源内容相似度检测，命中只标注不丢弃，交由下游/人工决定取舍。
            dup_of: str | None = None
            body_simhash: int | None = None
            if cfg.near_dup_check:
                body_simhash = cleaner.simhash(body)
                dup_of = manifest.find_near_duplicate(rel, body_simhash, cfg.near_dup_max_distance)

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
                near_duplicate_of=dup_of,
                injection_flagged=len(injection_flags) or None,
            )
            out_path.write_text(fm + body, encoding="utf-8")

            manifest.record(
                rel, digest, out_path.relative_to(cfg.output_root).as_posix(), converter_name,
                simhash=body_simhash,
            )
            summary.converted += 1
            note = f"near_duplicate_of={dup_of}" if dup_of else None
            summary.results.append(FileResult(rel, "converted", output_path=str(out_path), note=note))
    finally:
        manifest.close()

    return summary


@dataclass
class ScanEntry:
    rel_path: str
    ext: str
    size: int
    status: str  # "new" | "changed" | "unchanged"


def scan(cfg: IngestConfig) -> list[ScanEntry]:
    """列出 source_root 下会被 run 处理的文件清单，不做任何转换/落盘。

    供前端"先展现目录确认再填充 md"的预览步骤使用：与 run() 共用同一套
    扩展名/隐藏目录过滤规则，保证预览结果与实际转换范围一致。
    """
    manifest = Manifest(cfg.manifest_path)
    try:
        recorded = {r[0]: r[1] for r in manifest.all_records()}
        entries: list[ScanEntry] = []
        for src in _iter_source_files(cfg):
            rel = src.relative_to(cfg.source_root).as_posix()
            digest = sha256_file(src)
            if rel not in recorded:
                file_status = "new"
            elif recorded[rel] != digest:
                file_status = "changed"
            else:
                file_status = "unchanged"
            entries.append(ScanEntry(rel, src.suffix.lower(), src.stat().st_size, file_status))
        return entries
    finally:
        manifest.close()


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
                # 被质量过滤的记录 out_rel 为空字符串（未产出 md），不能拼成
                # output_root 本身去 unlink，否则会误删整个输出目录。
                if out_rel:
                    out_file = cfg.output_root / out_rel
                    if out_file.is_file():
                        out_file.unlink()
                manifest.remove(rel)
                removed += 1
    finally:
        manifest.close()
    return removed
