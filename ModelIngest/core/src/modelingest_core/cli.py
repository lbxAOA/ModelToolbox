"""ModelIngest 统一 CLI 入口。

融合 V1 和 V2 功能，提供简洁的命令接口。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main():
    """CLI 主入口。"""
    parser = argparse.ArgumentParser(
        prog="modelingest",
        description="多模态文档 → 结构化知识库转换器",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="ModelIngest 2.0.0",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令", required=True)
    
    # ============ 端到端命令 ============
    
    build_parser = subparsers.add_parser(
        "build",
        help="端到端构建知识库（推荐）",
    )
    build_parser.add_argument(
        "--source", "-s",
        type=Path,
        required=True,
        help="输入源：URL 或本地目录",
    )
    build_parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="输出知识库目录",
    )
    build_parser.add_argument(
        "--config",
        type=Path,
        help="配置文件路径（可选）",
    )
    build_parser.add_argument(
        "--visual",
        action="store_true",
        help="启用视觉渲染（网页截图）",
    )
    build_parser.add_argument(
        "--distill",
        action="store_true",
        help="启用知识蒸馏（需要 LLM）",
    )
    build_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="覆盖已存在的文件",
    )
    build_parser.add_argument(
        "--domain",
        default="通用",
        help="知识领域（影响蒸馏配置）",
    )
    
    # ============ 阶段命令 ============
    
    # discover: 发现链接（不下载）
    discover_parser = subparsers.add_parser(
        "discover",
        help="发现网页链接（不下载）",
    )
    discover_parser.add_argument(
        "--url", "-u",
        action="append",
        dest="urls",
        default=[],
        help="起始 URL（可重复）",
    )
    discover_parser.add_argument(
        "--urls-file",
        type=Path,
        help="URL 列表文件",
    )
    discover_parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="发现深度（默认：1）",
    )
    discover_parser.add_argument(
        "--max-pages",
        type=int,
        default=100,
        help="最大页面数（默认：100）",
    )
    discover_parser.add_argument(
        "--allow-cross-domain",
        action="store_true",
        help="允许跨域（默认：只同域）",
    )
    discover_parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式",
    )
    
    # crawl: 抓取网页
    crawl_parser = subparsers.add_parser(
        "crawl",
        help="抓取网页到本地",
    )
    crawl_parser.add_argument(
        "--url", "-u",
        action="append",
        dest="urls",
        default=[],
        help="URL（可重复）",
    )
    crawl_parser.add_argument(
        "--urls-file",
        type=Path,
        help="URL 列表文件",
    )
    crawl_parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="输出目录",
    )
    crawl_parser.add_argument(
        "--depth",
        type=int,
        default=0,
        help="抓取深度（0=仅指定URL）",
    )
    crawl_parser.add_argument(
        "--max-pages",
        type=int,
        default=200,
        help="最大页面数",
    )
    crawl_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="覆盖已存在文件",
    )
    
    # parse: 解析文档
    parse_parser = subparsers.add_parser(
        "parse",
        help="解析文档为 Markdown",
    )
    parse_parser.add_argument(
        "--source", "-s",
        type=Path,
        required=True,
        help="原始文档目录",
    )
    parse_parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Markdown 输出目录",
    )
    parse_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="覆盖已存在文件",
    )
    
    # distill: 知识蒸馏
    distill_parser = subparsers.add_parser(
        "distill",
        help="知识蒸馏（需要 LLM）",
    )
    distill_parser.add_argument(
        "--source", "-s",
        type=Path,
        required=True,
        help="Markdown 源目录",
    )
    distill_parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="知识库输出目录",
    )
    distill_parser.add_argument(
        "--profile",
        default="concept",
        choices=["concept", "algorithm"],
        help="蒸馏配置（默认：concept）",
    )
    distill_parser.add_argument(
        "--model",
        help="指定 LLM 模型",
    )
    distill_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="覆盖已存在笔记",
    )
    distill_parser.add_argument(
        "--no-link",
        action="store_true",
        help="不建立链接",
    )
    
    # guideline: 生成知识库准则
    guideline_parser = subparsers.add_parser(
        "guideline",
        help="生成知识库准则（蒸馏前配置）",
    )
    guideline_parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="知识库目录",
    )
    guideline_parser.add_argument(
        "--domain",
        default="通用",
        help="知识领域",
    )
    guideline_parser.add_argument(
        "--audience",
        default="rag_retrieval",
        choices=["self_review", "rag_retrieval", "training_data", "mixed"],
        help="目标受众",
    )
    guideline_parser.add_argument(
        "--granularity",
        default="medium",
        choices=["atomic", "medium", "long_form"],
        help="粒度",
    )
    guideline_parser.add_argument(
        "--interactive",
        action="store_true",
        help="交互式问答",
    )
    
    # ============ 工具命令 ============
    
    init_parser = subparsers.add_parser(
        "init",
        help="生成配置文件模板",
    )
    init_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("modelingest.yaml"),
        help="配置文件路径",
    )
    init_parser.add_argument(
        "--visual",
        action="store_true",
        help="启用视觉处理",
    )
    
    scan_parser = subparsers.add_parser(
        "scan",
        help="扫描并预览待处理文件",
    )
    scan_parser.add_argument(
        "--source", "-s",
        type=Path,
        required=True,
        help="源目录",
    )
    
    status_parser = subparsers.add_parser(
        "status",
        help="查看增量处理状态",
    )
    status_parser.add_argument(
        "--source", "-s",
        type=Path,
        required=True,
        help="源目录",
    )
    status_parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="输出目录",
    )
    
    clean_parser = subparsers.add_parser(
        "clean",
        help="清理缓存和临时文件",
    )
    clean_parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="输出目录",
    )
    
    args = parser.parse_args()
    
    # 导入处理函数（延迟导入避免启动慢）
    if args.command == "build":
        from .handlers import handle_build
        handle_build(args)
    elif args.command == "discover":
        from .handlers import handle_discover
        handle_discover(args)
    elif args.command == "crawl":
        from .handlers import handle_crawl
        handle_crawl(args)
    elif args.command == "parse":
        from .handlers import handle_parse
        handle_parse(args)
    elif args.command == "distill":
        from .handlers import handle_distill
        handle_distill(args)
    elif args.command == "guideline":
        from .handlers import handle_guideline
        handle_guideline(args)
    elif args.command == "init":
        from .handlers import handle_init
        handle_init(args)
    elif args.command == "scan":
        from .handlers import handle_scan
        handle_scan(args)
    elif args.command == "status":
        from .handlers import handle_status
        handle_status(args)
    elif args.command == "clean":
        from .handlers import handle_clean
        handle_clean(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())


def register(root: typer.Typer) -> None:
    """注册 ModelIngest CLI 到 ModelToolbox 主命令。"""
    try:
        import typer
    except ImportError:
        return

    ingest_app = typer.Typer(
        name="ingest",
        help="多模态文档 → 结构化知识库转换器",
        no_args_is_help=True,
    )

    @ingest_app.command("build")
    def build(
        source: Path = typer.Option(..., "--source", "-s", help="输入源：URL 或本地目录"),
        output: Path = typer.Option(..., "--output", "-o", help="输出知识库目录"),
        config: Path = typer.Option(None, "--config", help="配置文件路径（可选）"),
        visual: bool = typer.Option(False, "--visual", help="启用视觉渲染（网页截图）"),
        distill: bool = typer.Option(False, "--distill", help="启用知识蒸馏（需要 LLM）"),
        overwrite: bool = typer.Option(False, "--overwrite", help="覆盖已存在的文件"),
        domain: str = typer.Option("通用", "--domain", help="知识领域（影响蒸馏配置）"),
    ) -> None:
        """端到端构建知识库（推荐）"""
        from .handlers import handle_build
        import argparse

        args = argparse.Namespace(
            source=source,
            output=output,
            config=config,
            visual=visual,
            distill=distill,
            overwrite=overwrite,
            domain=domain,
        )
        handle_build(args)

    @ingest_app.command("version")
    def version() -> None:
        """显示 ModelIngest 版本"""
        typer.echo("ModelIngest 2.0.0")

    root.add_typer(ingest_app, name="ingest")
