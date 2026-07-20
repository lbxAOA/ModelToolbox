"""ModelIngest 命令行入口。

两段式管线：

阶段 A —— parse（原始文档 → 干净 md）::

    modelingest run    --source <原始文档目录> --output <md输出目录> [--no-pdf-pages] [--overwrite]
    modelingest status --source <...> --output <...>
    modelingest clean  --source <...> --output <...>

阶段 B —— distill（干净 md → 结构化原子笔记知识库，带 [[wikilink]] + MOC）::

    modelingest distill      --source <md目录> --output <知识库目录> [--profile concept|algorithm]
    modelingest distill-link --output <知识库目录>          # 只重跑建链 + MOC

原始文件始终留在 --source，不被移动或上传；转换产物写入 --output（镜像目录结构）。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import IngestConfig
from . import pipeline


def _add_common(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("--source", "-s", required=True, help="原始文档根目录（原件保留于此）")
    sp.add_argument("--output", "-o", required=True, help="Markdown 输出根目录")
    sp.add_argument(
        "--manifest",
        default=".ingest_cache/ingest_manifest.sqlite",
        help="增量 manifest 路径（默认相对 output）",
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="modelingest", description="原始文档 → Markdown 语料转换器")
    sub = p.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="执行转换（增量）")
    _add_common(run_p)
    run_p.add_argument("--overwrite", action="store_true", help="忽略 manifest，全量重转")
    run_p.add_argument("--no-pdf-pages", action="store_true", help="不抽取 PDF 页图")
    run_p.add_argument("--dpi", type=int, default=150, help="PDF 页图渲染 DPI")

    st_p = sub.add_parser("status", help="报告待转/已转/失效数量")
    _add_common(st_p)

    cl_p = sub.add_parser("clean", help="清理源已删除的记录与输出")
    _add_common(cl_p)

    # ---- 阶段 B：distill ----
    di_p = sub.add_parser("distill", help="把干净 md 蒸馏成结构化原子笔记知识库")
    di_p.add_argument("--source", "-s", required=True, help="解析后的 md 语料根目录")
    di_p.add_argument("--output", "-o", required=True, help="知识库(vault)输出根目录")
    di_p.add_argument("--profile", "-p", default="concept",
                      help="笔记模板：concept(默认) / algorithm")
    di_p.add_argument("--role", default="teacher", help="ModelProvider 角色（默认 teacher）")
    di_p.add_argument("--model", default=None,
                      help="覆盖模型，形如 provider:model（如 deepseek:deepseek-chat）")
    di_p.add_argument("--manifest", default=".distill_cache/distill_manifest.sqlite",
                      help="distill 增量 manifest 路径（默认相对 output）")
    di_p.add_argument("--overwrite", action="store_true", help="忽略 manifest，全量重蒸馏")
    di_p.add_argument("--no-link", action="store_true", help="跳过第二遍建链 + MOC 生成")

    dl_p = sub.add_parser("distill-link", help="只重跑第二遍：建 [[wikilink]] + 生成 MOC")
    dl_p.add_argument("--output", "-o", required=True, help="知识库(vault)根目录")

    return p


def _make_cfg(args) -> IngestConfig:
    return IngestConfig(
        source_root=Path(args.source),
        output_root=Path(args.output),
        manifest_path=Path(args.manifest),
        extract_pdf_pages=not getattr(args, "no_pdf_pages", False),
        pdf_page_dpi=getattr(args, "dpi", 150),
        overwrite=getattr(args, "overwrite", False),
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command in {"run", "status", "clean"}:
        cfg = _make_cfg(args)

    if args.command == "run":
        summary = pipeline.run(cfg)
        print(f"✅ 转换 {summary.converted} · 跳过 {summary.skipped} · 失败 {summary.failed}")
        for r in summary.results:
            if r.status == "failed":
                print(f"  ✗ {r.rel_path}: {r.error}", file=sys.stderr)
        return 1 if summary.failed else 0

    if args.command == "status":
        s = pipeline.status(cfg)
        print(f"已记录 {s['recorded']} · 待转(新) {s['pending_new']} · "
              f"待转(变更) {s['pending_changed']} · 源已删 {s['stale_source_deleted']}")
        for rel in s["stale_list"]:
            print(f"  (stale) {rel}")
        return 0

    if args.command == "clean":
        n = pipeline.clean(cfg)
        print(f"🧹 清理 {n} 条失效记录")
        return 0

    if args.command == "distill":
        from .distill import DistillConfig, TeacherUnavailable, run as distill_run
        dcfg = DistillConfig(
            source_root=Path(args.source),
            vault_root=Path(args.output),
            profile=args.profile,
            role=args.role,
            model=args.model,
            manifest_path=Path(args.manifest),
            overwrite=args.overwrite,
            do_link=not args.no_link,
        )
        try:
            s = distill_run(dcfg)
        except TeacherUnavailable as exc:
            print(f"✗ {exc}", file=sys.stderr)
            return 1
        except KeyError as exc:  # 未知 profile
            print(f"✗ {exc}", file=sys.stderr)
            return 2
        print(f"✅ 蒸馏源 {s.distilled} · 跳过 {s.skipped} · 产出笔记 {s.notes} · 失败 {s.failed}")
        if s.link_stats:
            ls = s.link_stats
            print(f"🔗 建链 {ls['relinked']} 篇 · MOC {ls['mocs']} 个 · 标题索引 {ls['titles']}")
        for e in s.errors[:20]:
            print(f"  ! {e}", file=sys.stderr)
        return 1 if (s.failed and not s.notes) else 0

    if args.command == "distill-link":
        from .distill import link_only
        stats = link_only(Path(args.output))
        print(f"🔗 建链 {stats['relinked']} 篇 · MOC {stats['mocs']} 个 · 标题索引 {stats['titles']}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
