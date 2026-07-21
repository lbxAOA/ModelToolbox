"""ModelIngest 命令行入口。

两段式管线（外加阶段 A 前置的可选抓取）：

阶段 A 前置 —— crawl（抓取公开网页/文件到本地，产物是原始 .html/.pdf/...）::

    modelingest crawl --url <URL> [--url <URL> ...] --output <原始文档目录> \
        [--urls-file <文件>] [--depth 0] [--ignore-robots] [--overwrite]

阶段 A —— parse（原始文档 → 干净 md）::

    modelingest run    --source <原始文档目录> --output <md输出目录> [--no-pdf-pages] [--overwrite]
    modelingest status --source <...> --output <...>
    modelingest clean  --source <...> --output <...>

阶段 B —— distill（干净 md → 结构化原子笔记知识库，带 [[wikilink]] + MOC）::

    modelingest distill      --source <md目录> --output <知识库目录> [--profile concept|algorithm]
    modelingest distill-link --output <知识库目录>          # 只重跑建链 + MOC

原始文件始终留在 --source，不被移动或上传；转换产物写入 --output（镜像目录结构）。
crawl 的 --output 通常就指向某个 source_root（或其子目录），抓下来的原始文件随后
可直接被 `modelingest run` 当作本地文档一样转换。
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

    # ---- 阶段 A 前置：crawl ----
    cr_p = sub.add_parser("crawl", help="抓取公开网页/文件到本地（产物随后可用 run 正常转换）")
    cr_p.add_argument("--url", "-u", action="append", dest="urls", default=[],
                       help="要抓取的 URL（可重复传入）")
    cr_p.add_argument("--urls-file", help="URL 列表文件，每行一个（# 开头视为注释）")
    cr_p.add_argument("--output", "-o", required=True, help="抓取产物输出目录（通常是 source_root 的子目录）")
    cr_p.add_argument("--manifest", default=".crawl_cache/crawl_manifest.sqlite",
                       help="crawl 增量 manifest 路径（默认相对 output）")
    cr_p.add_argument("--depth", type=int, default=0, help="跟随链接抓取的深度（0=只抓给定 URL）")
    cr_p.add_argument("--allow-cross-domain", action="store_true", help="跟随链接时允许跨域（默认只抓同域）")
    cr_p.add_argument("--delay", type=float, default=1.0, help="请求间隔秒数（礼貌抓取）")
    cr_p.add_argument("--timeout", type=float, default=20.0, help="单次请求超时秒数")
    cr_p.add_argument("--max-pages", type=int, default=200, help="本次运行最多抓取的页面数（安全上限）")
    cr_p.add_argument("--ignore-robots", action="store_true", help="忽略 robots.txt（默认遵守，谨慎使用）")
    cr_p.add_argument("--overwrite", action="store_true", help="忽略 manifest，强制重新抓取")
    cr_p.add_argument("--user-agent", default=None, help="自定义 User-Agent")

    run_p = sub.add_parser("run", help="执行转换（增量）")
    _add_common(run_p)
    run_p.add_argument("--overwrite", action="store_true", help="忽略 manifest，全量重转")
    run_p.add_argument("--no-pdf-pages", action="store_true", help="不抽取 PDF 页图")
    run_p.add_argument("--dpi", type=int, default=150, help="PDF 页图渲染 DPI")
    run_p.add_argument("--no-html-clean", action="store_true", help="不做网页正文去噪（保留 nav/广告等样板内容）")
    run_p.add_argument("--no-injection-scan", action="store_true", help="不做 prompt injection 隔离标记")
    run_p.add_argument("--no-quality-filter", action="store_true", help="不过滤空内容/登录墙/错误页等低质量源")
    run_p.add_argument("--no-dedup", action="store_true", help="不做跨来源近似去重检测")
    run_p.add_argument("--dedup-distance", type=int, default=3, help="近似去重 SimHash 汉明距离阈值（默认 3/64 bit）")

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
        clean_html=not getattr(args, "no_html_clean", False),
        neutralize_injection=not getattr(args, "no_injection_scan", False),
        quality_filter=not getattr(args, "no_quality_filter", False),
        near_dup_check=not getattr(args, "no_dedup", False),
        near_dup_max_distance=getattr(args, "dedup_distance", 3),
    )


def _collect_crawl_urls(args) -> list[str]:
    urls = list(args.urls or [])
    if args.urls_file:
        text = Path(args.urls_file).read_text(encoding="utf-8")
        urls.extend(
            line.strip() for line in text.splitlines()
            if line.strip() and not line.strip().startswith("#")
        )
    return urls


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "crawl":
        from .crawler import CrawlConfig, DEFAULT_USER_AGENT, crawl as crawl_run

        urls = _collect_crawl_urls(args)
        if not urls:
            print("✗ 请通过 --url 或 --urls-file 提供至少一个 URL", file=sys.stderr)
            return 2

        ccfg = CrawlConfig(
            urls=urls,
            output_root=Path(args.output),
            manifest_path=Path(args.manifest),
            max_depth=args.depth,
            same_domain_only=not args.allow_cross_domain,
            delay=args.delay,
            timeout=args.timeout,
            user_agent=args.user_agent or DEFAULT_USER_AGENT,
            respect_robots=not args.ignore_robots,
            overwrite=args.overwrite,
            max_pages=args.max_pages,
        )
        summary = crawl_run(ccfg)
        print(f"✅ 抓取 {summary.fetched} · 跳过 {summary.skipped} · 失败 {summary.failed}")
        for r in summary.results:
            if r.status == "failed":
                print(f"  ✗ {r.url}: {r.error}", file=sys.stderr)
        return 1 if (summary.failed and not summary.fetched) else 0

    if args.command in {"run", "status", "clean"}:
        cfg = _make_cfg(args)

    if args.command == "run":
        summary = pipeline.run(cfg)
        print(
            f"✅ 转换 {summary.converted} · 跳过 {summary.skipped} · "
            f"过滤 {summary.filtered} · 失败 {summary.failed}"
        )
        for r in summary.results:
            if r.status == "failed":
                print(f"  ✗ {r.rel_path}: {r.error}", file=sys.stderr)
            elif r.status == "filtered":
                print(f"  ⚠ {r.rel_path}: 已过滤（{r.error}）")
            elif r.note:
                print(f"  ℹ {r.rel_path}: {r.note}")
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
