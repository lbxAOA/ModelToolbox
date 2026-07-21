"""ModelIngest 命令行入口。

两段式管线（外加阶段 A 前置的可选抓取、阶段 B 前置的可选知识库准则问答）：

阶段 A 前置 —— discover（只发现分支页面目录，不落盘，供确认后再 crawl）::

    modelingest discover --url <URL> [--url <URL> ...] [--depth 1] [--max-pages 100]

阶段 A 前置 —— crawl（抓取公开网页/文件到本地，产物是原始 .html/.pdf/...）::

    modelingest crawl --url <URL> [--url <URL> ...] --output <原始文档目录> \
        [--urls-file <文件>] [--depth 0] [--ignore-robots] [--overwrite]

阶段 A —— parse（原始文档 → 干净 md）::

    modelingest scan   --source <本地目录> --output <...>            # 只预览会被转换的文件清单，不落盘
    modelingest run    --source <原始文档目录> --output <md输出目录> [--include <相对路径> ...] [--overwrite]
    modelingest status --source <...> --output <...>
    modelingest clean  --source <...> --output <...>

阶段 B 前置 —— guideline（通过几个问题了解需求，生成蒸馏时使用的知识库准则）::

    modelingest guideline --output <知识库目录> \
        [--domain ...] [--audience self_review|rag_retrieval|training_data|mixed] \
        [--granularity atomic|medium|long_form] [--language zh|en|bilingual] \
        [--keep-formulas-code true|false] [--extra-notes ...] [--interactive]

    不传任何问题 flag（或加 --interactive）时在终端逐条交互式提问；webui 等程序化
    调用方应直接传齐 flag。生成的 GUIDELINE.md 写入 <知识库目录>/.ingest_meta/，
    distill 时自动探测并附加给 teacher（无论 Ollama 还是闭源模型都适用）。

阶段 B —— distill（干净 md → 结构化原子笔记知识库，带 [[wikilink]] + MOC）::

    modelingest distill      --source <md目录> --output <知识库目录> [--profile concept|algorithm] \
        [--guideline <准则文件路径，缺省自动探测 output/.ingest_meta/GUIDELINE.md>]
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

    # ---- 阶段 A 前置：discover（只发现分支页面目录，不落盘） ----
    ds_p = sub.add_parser("discover", help="发现网址下的分支页面目录（不落盘），供确认后再 crawl")
    ds_p.add_argument("--url", "-u", action="append", dest="urls", default=[],
                       help="起始 URL（可重复传入）")
    ds_p.add_argument("--urls-file", help="URL 列表文件，每行一个（# 开头视为注释）")
    ds_p.add_argument("--depth", type=int, default=1, help="跟随分支链接发现的深度（默认 1）")
    ds_p.add_argument("--allow-cross-domain", action="store_true", help="跟随链接时允许跨域（默认只发现同域）")
    ds_p.add_argument("--delay", type=float, default=0.5, help="请求间隔秒数（礼貌抓取）")
    ds_p.add_argument("--timeout", type=float, default=20.0, help="单次请求超时秒数")
    ds_p.add_argument("--max-pages", type=int, default=100, help="本次最多发现的页面数（安全上限）")
    ds_p.add_argument("--ignore-robots", action="store_true", help="忽略 robots.txt（默认遵守，谨慎使用）")
    ds_p.add_argument("--user-agent", default=None, help="自定义 User-Agent")

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
    run_p.add_argument("--include", action="append", dest="include", default=None,
                       help="只转换指定的相对路径（可重复；缺省转换全部匹配文件）")
    run_p.add_argument("--no-pdf-pages", action="store_true", help="不抽取 PDF 页图")
    run_p.add_argument("--dpi", type=int, default=150, help="PDF 页图渲染 DPI")
    run_p.add_argument("--no-html-clean", action="store_true", help="不做网页正文去噪（保留 nav/广告等样板内容）")
    run_p.add_argument("--no-injection-scan", action="store_true", help="不做 prompt injection 隔离标记")
    run_p.add_argument("--no-quality-filter", action="store_true", help="不过滤空内容/登录墙/错误页等低质量源")
    run_p.add_argument("--no-dedup", action="store_true", help="不做跨来源近似去重检测")
    run_p.add_argument("--dedup-distance", type=int, default=3, help="近似去重 SimHash 汉明距离阈值（默认 3/64 bit）")

    sc_p = sub.add_parser("scan", help="预览本地目录会被转换的文件清单（不落盘，供确认后再 run）")
    _add_common(sc_p)

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
    di_p.add_argument("--guideline", default=None,
                      help="知识库准则文件路径（默认自动探测 output/.ingest_meta/GUIDELINE.md，"
                           "由 `modelingest guideline` 生成；不存在则不使用准则）")
    di_p.add_argument("--overwrite", action="store_true", help="忽略 manifest，全量重蒸馏")
    di_p.add_argument("--no-link", action="store_true", help="跳过第二遍建链 + MOC 生成")

    dl_p = sub.add_parser("distill-link", help="只重跑第二遍：建 [[wikilink]] + 生成 MOC")
    dl_p.add_argument("--output", "-o", required=True, help="知识库(vault)根目录")

    # ---- 阶段 B 前置：guideline（通过几个问题了解需求，生成蒸馏时使用的准则） ----
    gl_p = sub.add_parser("guideline", help="生成/更新一份知识库蒸馏准则（GUIDELINE.md）")
    gl_p.add_argument("--output", "-o", required=True, help="知识库(vault)根目录（准则写入 <output>/.ingest_meta/）")
    gl_p.add_argument("--domain", default=None, help="领域/用途，如“算法竞赛”“电路板设计”")
    gl_p.add_argument("--audience", default=None, choices=["self_review", "rag_retrieval", "training_data", "mixed"],
                      help="主要使用场景")
    gl_p.add_argument("--granularity", default=None, choices=["atomic", "medium", "long_form"],
                      help="笔记粒度偏好")
    gl_p.add_argument("--language", default=None, choices=["zh", "en", "bilingual"], help="笔记语言风格")
    gl_p.add_argument("--keep-formulas-code", dest="keep_formulas_code", default=None,
                      choices=["true", "false"], help="是否完整保留原文公式/代码")
    gl_p.add_argument("--extra-notes", dest="extra_notes", default=None, help="其它特殊要求（可选）")
    gl_p.add_argument("--interactive", action="store_true",
                      help="未通过 flag 提供的问题改为在终端交互式询问（webui 不用，人工 CLI 可用）")

    # ---- B 部分收尾：为荒馆新蒸馆好的知识库自动生成一个 ModelSkill 技能 ----
    mk_p = sub.add_parser("make-skill", help="为一个知识库自动生成/注册一个检索技能（ModelSkill）")
    mk_p.add_argument("--name", required=True, help="知识库名称（会被 slug 化作为技能标识）")
    mk_p.add_argument("--description", required=True, help="一句话描述（会拼入触发词）")
    mk_p.add_argument("--triggers", default="", help="逗号分隔的触发词")
    mk_p.add_argument("--vault", required=True, help="知识库(vault)根目录")
    mk_p.add_argument("--source", required=True, help="原始 md 语料目录")
    mk_p.add_argument("--model-spec", default="", help="蒸馆用的 provider:model 或 role（仅用于写入技能说明）")
    mk_p.add_argument("--profile", default="concept", help="笔记模板（仅用于写入技能说明）")

    return p


def _make_cfg(args) -> IngestConfig:
    include = getattr(args, "include", None)
    return IngestConfig(
        source_root=Path(args.source),
        output_root=Path(args.output),
        manifest_path=Path(args.manifest),
        extract_pdf_pages=not getattr(args, "no_pdf_pages", False),
        pdf_page_dpi=getattr(args, "dpi", 150),
        overwrite=getattr(args, "overwrite", False),
        include=set(include) if include else None,
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

    if args.command == "discover":
        import json

        from .crawler import DiscoverConfig, DEFAULT_USER_AGENT, discover as discover_run

        urls = _collect_crawl_urls(args)
        if not urls:
            print("✗ 请通过 --url 或 --urls-file 提供至少一个 URL", file=sys.stderr)
            return 2

        dcfg = DiscoverConfig(
            urls=urls,
            max_depth=args.depth,
            same_domain_only=not args.allow_cross_domain,
            delay=args.delay,
            timeout=args.timeout,
            user_agent=args.user_agent or DEFAULT_USER_AGENT,
            respect_robots=not args.ignore_robots,
            max_pages=args.max_pages,
        )
        result = discover_run(dcfg)
        print(f"✅ 发现 {result.total} 个页面 · 可用 {result.ok} · 失败 {result.failed}")
        catalog = [
            {
                "url": e.url,
                "depth": e.depth,
                "parent": e.parent,
                "title": e.title,
                "status": e.status,
                "error": e.error,
            }
            for e in result.entries
        ]
        # 前端从任务日志里抓取这一行解析出目录，供用户勾选确认后再调用 crawl。
        print("@@CATALOG_JSON@@" + json.dumps(catalog, ensure_ascii=False))
        return 0

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

    if args.command in {"run", "scan", "status", "clean"}:
        cfg = _make_cfg(args)

    if args.command == "scan":
        import json

        entries = pipeline.scan(cfg)
        print(f"✅ 发现 {len(entries)} 个可转换文件")
        catalog = [
            {"path": e.rel_path, "ext": e.ext, "size": e.size, "status": e.status}
            for e in entries
        ]
        # 前端从任务日志里抓取这一行解析出目录，供用户勾选确认后再调用 run --include。
        print("@@CATALOG_JSON@@" + json.dumps(catalog, ensure_ascii=False))
        return 0

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
            guideline_path=Path(args.guideline) if args.guideline else None,
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

    if args.command == "guideline":
        from . import guideline as guideline_mod

        flag_answers = {
            "domain": args.domain,
            "audience": args.audience,
            "granularity": args.granularity,
            "language": args.language,
            "keep_formulas_code": args.keep_formulas_code,
            "extra_notes": args.extra_notes,
        }
        # 只保留真正传了的 flag；None 表示未传，交给交互/默认值补全。
        given = {k: v for k, v in flag_answers.items() if v is not None}
        if args.interactive or not given:
            answers = guideline_mod.prompt_interactive(given)
        else:
            answers = given
        try:
            result = guideline_mod.generate_and_save(Path(args.output), answers)
        except ValueError as exc:
            print(f"✗ {exc}", file=sys.stderr)
            return 2
        print(f"✅ 已生成知识库准则 -> {result.guideline_path}")
        print("   distill 时会自动探测并遵循此准则（可直接编辑该文件调整规则，无需重新回答问题）。")
        return 0

    if args.command == "make-skill":
        from .skillgen import SkillGenError, generate_knowledge_base_skill
        try:
            result = generate_knowledge_base_skill(
                name=args.name,
                description=args.description,
                triggers=args.triggers,
                vault_root=Path(args.vault),
                source_root=Path(args.source),
                model_spec=args.model_spec,
                profile=args.profile,
            )
        except SkillGenError as exc:
            print(f"✗ {exc}", file=sys.stderr)
            return 1
        print(f"✅ 已生成技能 '{result.name}' -> {result.skill_path}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
