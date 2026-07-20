"""distill 编排：解析后的 md 语料 → 结构化原子笔记知识库。

流程（阶段 B）::

    raw_md/**/*.md
      └─(chunk)→ 概念块
             └─(teacher)→ 受约束 JSON
                    └─(validate)→ 规范化 note
                           └─(render)→ Algorithms 版式 md 卡片
      之后统一 (linker) 建 [[wikilink]] + 生成 MOC

- 增量：源 md 的 hash + profile 未变则跳过（DistillManifest）。
- teacher 不可用（未装 ModelProvider）时抛 TeacherUnavailable，由 CLI 友好提示。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from ..manifest import sha256_file
from . import linker as _linker
from .chunk import chunk_markdown
from .dmanifest import DistillManifest
from .profiles import Profile, get_profile
from .render import render_note
from .teacher import (
    Teacher,
    build_prompt,
    build_system,
    build_teacher,
    extract_json,
)
from .validate import NoteValidationError, validate_notes


@dataclass
class DistillConfig:
    source_root: Path                 # 解析后的 md 语料根（阶段 A 的 output）
    vault_root: Path                  # 知识库输出根
    profile: str = "concept"
    role: str = "teacher"
    model: str | None = None
    manifest_path: Path = field(default=Path(".distill_cache/distill_manifest.sqlite"))
    overwrite: bool = False
    do_link: bool = True
    min_chars: int = 400
    max_chars: int = 6000

    def __post_init__(self) -> None:
        self.source_root = Path(self.source_root).resolve()
        self.vault_root = Path(self.vault_root).resolve()
        self.manifest_path = Path(self.manifest_path)
        if not self.manifest_path.is_absolute():
            self.manifest_path = (self.vault_root / self.manifest_path).resolve()


@dataclass
class DistillSummary:
    distilled: int = 0        # 处理的源 md 数
    skipped: int = 0
    notes: int = 0            # 产出笔记数
    failed: int = 0
    link_stats: dict | None = None
    errors: list[str] = field(default_factory=list)


_SLUG = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _safe_filename(title: str) -> str:
    name = _SLUG.sub("", title).strip().rstrip(".")
    return name or "Untitled"


def _iter_md(root: Path):
    for p in sorted(root.rglob("*.md")):
        if not p.is_file():
            continue
        if any(part.startswith(".") for part in p.relative_to(root).parts):
            continue
        if p.stem.endswith("MOC"):
            continue
        yield p


def _model_label(cfg: DistillConfig) -> str:
    return cfg.model or f"role:{cfg.role}"


def distill_file(
    src: Path,
    cfg: DistillConfig,
    profile: Profile,
    teacher: Teacher,
) -> tuple[list[Path], list[str]]:
    """蒸馏单个源 md，返回 (写出的笔记路径列表, 错误列表)。"""
    rel = src.relative_to(cfg.source_root)
    # 输出目录：镜像源相对目录（去掉文件名那层用其父目录）。
    out_dir = (cfg.vault_root / rel).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    parent_moc = f"{out_dir.name} MOC" if out_dir != cfg.vault_root else "Knowledge Base MOC"

    md_text = src.read_text(encoding="utf-8", errors="replace")
    doc_title = src.stem
    chunks = chunk_markdown(md_text, min_chars=cfg.min_chars, max_chars=cfg.max_chars)

    written: list[Path] = []
    errors: list[str] = []
    seen_titles: set[str] = set()

    for ch in chunks:
        prompt = build_prompt(profile, ch.text, doc_title=doc_title)
        try:
            raw = teacher(prompt, build_system())
            payload = extract_json(raw)
            notes = validate_notes(payload, profile)
        except (ValueError, NoteValidationError) as exc:
            errors.append(f"{rel} #chunk{ch.index}: {exc}")
            continue
        except Exception as exc:  # noqa: BLE001 - teacher 网络/供应商异常
            errors.append(f"{rel} #chunk{ch.index}: teacher 调用失败: {exc}")
            continue

        for note in notes:
            title = note["title"]
            key = title.lower()
            if key in seen_titles:
                continue
            seen_titles.add(key)
            md = render_note(
                note,
                profile,
                parent_moc=parent_moc,
                source=rel.as_posix(),
                generated_by=_model_label(cfg),
            )
            out_path = out_dir / f"{_safe_filename(title)}.md"
            out_path.write_text(md, encoding="utf-8")
            written.append(out_path)

    return written, errors


def run(cfg: DistillConfig) -> DistillSummary:
    """执行阶段 B。"""
    cfg.vault_root.mkdir(parents=True, exist_ok=True)
    profile = get_profile(cfg.profile)
    teacher = build_teacher(role=cfg.role, model=cfg.model)  # 可能抛 TeacherUnavailable

    manifest = DistillManifest(cfg.manifest_path)
    summary = DistillSummary()
    try:
        for src in _iter_md(cfg.source_root):
            rel = src.relative_to(cfg.source_root).as_posix()
            digest = sha256_file(src)
            if not cfg.overwrite and not manifest.needs_distill(rel, digest, cfg.profile):
                summary.skipped += 1
                continue

            written, errors = distill_file(src, cfg, profile, teacher)
            summary.errors.extend(errors)
            if written:
                summary.distilled += 1
                summary.notes += len(written)
                rels = [p.relative_to(cfg.vault_root).as_posix() for p in written]
                manifest.record(rel, digest, cfg.profile, rels)
            else:
                summary.failed += 1
    finally:
        manifest.close()

    if cfg.do_link:
        summary.link_stats = _linker.link_vault(
            cfg.vault_root, generated_by="ModelIngest"
        )
    return summary


def link_only(vault_root: Path) -> dict:
    """只重跑第二遍（建链 + MOC）。"""
    return _linker.link_vault(Path(vault_root), generated_by="ModelIngest")
