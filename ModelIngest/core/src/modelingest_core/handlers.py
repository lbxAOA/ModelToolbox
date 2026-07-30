"""CLI 命令处理函数。"""

from __future__ import annotations

import json
import sys
from argparse import Namespace
from pathlib import Path


def _collect_urls(url_list: list[str], urls_file: Path | None) -> list[str]:
    """收集 URL 列表。"""
    urls = list(url_list)
    if urls_file:
        text = urls_file.read_text(encoding="utf-8")
        urls.extend(
            line.strip()
            for line in text.splitlines()
            if line.strip() and not line.strip().startswith("#")
        )
    return urls


def handle_discover(args: Namespace):
    """处理 discover 命令。"""
    from modelingest_fetch import discover, DiscoverConfig
    
    urls = _collect_urls(args.urls, args.urls_file)
    if not urls:
        print("错误：需要至少一个 URL（--url 或 --urls-file）", file=sys.stderr)
        sys.exit(1)
    
    cfg = DiscoverConfig(
        urls=urls,
        max_depth=args.depth,
        same_domain_only=not args.allow_cross_domain,
        max_pages=args.max_pages,
    )
    
    result = discover(cfg)
    
    if args.json:
        data = {
            "total": result.total,
            "ok": result.ok,
            "failed": result.failed,
            "entries": [
                {
                    "url": e.url,
                    "depth": e.depth,
                    "parent": e.parent,
                    "title": e.title,
                    "status": e.status,
                    "error": e.error,
                }
                for e in result.entries
            ],
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"发现 {result.total} 个页面，成功 {result.ok}，失败 {result.failed}")
        for entry in result.entries:
            indent = "  " * entry.depth
            status_icon = "✓" if entry.status == "ok" else "✗"
            print(f"{indent}{status_icon} {entry.url}")
            if entry.title:
                print(f"{indent}   {entry.title}")


def handle_crawl(args: Namespace):
    """处理 crawl 命令。"""
    from modelingest_fetch import crawl, CrawlConfig
    
    urls = _collect_urls(args.urls, args.urls_file)
    if not urls:
        print("错误：需要至少一个 URL", file=sys.stderr)
        sys.exit(1)
    
    cfg = CrawlConfig(
        urls=urls,
        output_root=args.output,
        max_depth=args.depth,
        max_pages=args.max_pages,
        overwrite=args.overwrite,
    )
    
    result = crawl(cfg)
    
    print(f"抓取完成：")
    print(f"  下载：{result.fetched} 个文件")
    print(f"  跳过：{result.skipped} 个文件")
    print(f"  失败：{result.failed} 个文件")


def handle_parse(args: Namespace):
    """处理 parse 命令。"""
    print("parse 命令待实现")
    # TODO: 实现 parse 逻辑


def handle_distill(args: Namespace):
    """处理 distill 命令。"""
    from modelingest_distill import run, DistillConfig
    
    cfg = DistillConfig(
        source_root=args.source,
        vault_root=args.output,
        profile=args.profile,
        model=args.model,
        overwrite=args.overwrite,
        do_link=not args.no_link,
    )
    
    try:
        result = run(cfg)
        print(f"蒸馏完成：")
        print(f"  处理：{result.distilled} 个文件")
        print(f"  跳过：{result.skipped} 个文件")
        print(f"  生成：{result.notes} 个笔记")
        if result.failed:
            print(f"  失败：{result.failed} 个文件")
        if result.link_stats:
            print(f"  链接：{result.link_stats}")
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


def handle_guideline(args: Namespace):
    """处理 guideline 命令。"""
    print("guideline 命令待实现")
    # TODO: 实现 guideline 逻辑


def handle_build(args: Namespace):
    """处理 build 命令。"""
    print("build 命令待实现")
    # TODO: 实现完整管道


def handle_init(args: Namespace):
    """处理 init 命令。"""
    print("init 命令待实现")
    # TODO: 生成配置文件模板


def handle_scan(args: Namespace):
    """处理 scan 命令。"""
    print("scan 命令待实现")


def handle_status(args: Namespace):
    """处理 status 命令。"""
    print("status 命令待实现")


def handle_clean(args: Namespace):
    """处理 clean 命令。"""
    print("clean 命令待实现")
