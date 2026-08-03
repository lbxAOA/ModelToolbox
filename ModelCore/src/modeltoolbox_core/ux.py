"""用户体验改进工具：初始化、检查、示例"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import typer

from modeltoolbox_core.config import get_state_dir
from modeltoolbox_core.jsonio import print_json


ux_app = typer.Typer(help="用户体验改进工具", no_args_is_help=True)


@ux_app.command("init")
def init_config(
    force: bool = typer.Option(False, "--force", help="覆盖已存在的配置"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="交互式配置"),
) -> None:
    """初始化 ModelToolbox 配置文件"""
    state_dir = get_state_dir()
    config_dir = state_dir / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    # Provider 配置
    provider_config = config_dir / "provider.json"
    if not provider_config.exists() or force:
        if interactive:
            typer.echo("🔧 配置 Provider...")
            default_provider = typer.prompt("默认 provider", default="ollama")
            ollama_url = typer.prompt("Ollama URL", default="http://127.0.0.1:11434")
            ollama_model = typer.prompt("Ollama 默认模型", default="llama3.2")
        else:
            default_provider = "ollama"
            ollama_url = "http://127.0.0.1:11434"
            ollama_model = "llama3.2"

        config = {
            "default_provider": default_provider,
            "providers": {
                "ollama": {
                    "base_url": ollama_url,
                    "model": ollama_model,
                    "timeout": 60.0,
                },
                "anthropic": {
                    "api_key": "${ANTHROPIC_API_KEY}",
                    "model": "claude-3-5-sonnet-20241022",
                    "timeout": 120.0,
                },
            },
        }
        provider_config.write_text(json.dumps(config, indent=2, ensure_ascii=False))
        typer.echo(f"✅ Provider 配置已创建: {provider_config}")

    # Ingest 配置
    ingest_config = config_dir / "ingest.json"
    if not ingest_config.exists() or force:
        config = {
            "default_quality": "medium",
            "default_structure": "obsidian",
            "crawl": {
                "max_pages": 500,
                "delay": 0.5,
                "timeout": 20.0,
            },
        }
        ingest_config.write_text(json.dumps(config, indent=2, ensure_ascii=False))
        typer.echo(f"✅ Ingest 配置已创建: {ingest_config}")

    # Office 配置
    office_config = config_dir / "office.json"
    if not office_config.exists() or force:
        config = {
            "default_timeout": 60.0,
            "default_network": True,
            "python_version": "3.11",
        }
        office_config.write_text(json.dumps(config, indent=2, ensure_ascii=False))
        typer.echo(f"✅ Office 配置已创建: {office_config}")

    typer.echo("\n🎉 配置初始化完成！")
    typer.echo(f"配置目录: {config_dir}")


@ux_app.command("check")
def check_environment() -> None:
    """检查运行环境和依赖"""
    typer.echo("🔍 检查 ModelToolbox 环境...\n")

    checks: list[tuple[str, bool, str]] = []

    # Python 版本
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 11)
    checks.append(("Python 版本", py_ok, f"{py_version} {'✅' if py_ok else '❌ (需要 >= 3.11)'}"))

    # 状态目录
    state_dir = get_state_dir()
    state_ok = state_dir.exists()
    checks.append(("状态目录", state_ok, f"{state_dir} {'✅' if state_ok else '❌'}"))

    # 配置文件
    config_dir = state_dir / "config"
    provider_config = config_dir / "provider.json"
    config_ok = provider_config.exists()
    checks.append(
        (
            "Provider 配置",
            config_ok,
            f"{'✅ 已配置' if config_ok else '❌ 未配置 (运行 mtb ux init)'}",
        )
    )

    # Git
    import shutil

    git_path = shutil.which("git")
    git_ok = git_path is not None
    checks.append(("Git", git_ok, f"{'✅ ' + git_path if git_ok else '❌ 未安装'}"))

    # Ollama (可选)
    import subprocess

    try:
        result = subprocess.run(
            ["curl", "-s", "http://127.0.0.1:11434/api/tags"],
            capture_output=True,
            timeout=2,
        )
        ollama_ok = result.returncode == 0
    except Exception:
        ollama_ok = False
    checks.append(
        (
            "Ollama (可选)",
            ollama_ok,
            f"{'✅ 运行中' if ollama_ok else '⚠️  未运行 (本地模型需要)'}",
        )
    )

    # 打印结果
    for name, ok, msg in checks:
        icon = "✅" if ok else "❌"
        typer.echo(f"{icon} {name}: {msg}")

    # 总结
    all_critical_ok = all(ok for name, ok, _ in checks[:4])  # 前 4 项是关键的
    typer.echo()
    if all_critical_ok:
        typer.echo("🎉 环境检查通过！")
    else:
        typer.echo("⚠️  环境有问题，请修复后再使用。")
        sys.exit(1)


@ux_app.command("examples")
def show_examples(
    category: str = typer.Argument(None, help="示例类别: ingest, provider, office, memory"),
) -> None:
    """显示使用示例"""
    examples = {
        "ingest": {
            "title": "📄 文档摄取示例",
            "examples": [
                {
                    "desc": "从网站构建知识库",
                    "cmd": "mtb ingest build --source https://docs.example.com --output ./vault/docs",
                },
                {
                    "desc": "从本地目录摄取",
                    "cmd": "mtb ingest build --source ./raw-docs --output ./vault --quality high",
                },
                {
                    "desc": "爬取网站",
                    "cmd": "mtb ingest crawl --url https://example.com --output ./raw --depth 2",
                },
            ],
        },
        "provider": {
            "title": "🤖 模型 Provider 示例",
            "examples": [
                {
                    "desc": "使用 Ollama 聊天",
                    "cmd": "mtb provider chat --message 'Hello' --model llama3.2",
                },
                {
                    "desc": "流式响应",
                    "cmd": "mtb provider chat-stream --message 'Write a story' --model llama3.2",
                },
                {
                    "desc": "使用 Claude",
                    "cmd": "mtb provider chat --provider anthropic --message 'Explain quantum computing'",
                },
                {
                    "desc": "生成嵌入",
                    "cmd": "mtb provider embed --text 'Hello world' --model llama3.2",
                },
            ],
        },
        "office": {
            "title": "🔒 沙箱执行示例",
            "examples": [
                {
                    "desc": "创建环境",
                    "cmd": "mtb office env create ml-env",
                },
                {
                    "desc": "安装依赖",
                    "cmd": "mtb office install ml-env numpy pandas",
                },
                {
                    "desc": "执行代码",
                    "cmd": "mtb office exec ml-env python script.py",
                },
                {
                    "desc": "禁用网络",
                    "cmd": "mtb office exec ml-env python sensitive.py --no-network",
                },
            ],
        },
        "memory": {
            "title": "🔍 本地索引示例",
            "examples": [
                {
                    "desc": "索引目录",
                    "cmd": "mtb memory index ./vault --include '*.md'",
                },
                {
                    "desc": "搜索内容",
                    "cmd": "mtb memory search 'authentication' --limit 5",
                },
                {
                    "desc": "查看统计",
                    "cmd": "mtb memory stats --json",
                },
            ],
        },
    }

    if category:
        if category not in examples:
            typer.echo(f"❌ 未知类别: {category}")
            typer.echo(f"可用类别: {', '.join(examples.keys())}")
            sys.exit(1)

        cat = examples[category]
        typer.echo(f"\n{cat['title']}\n")
        for ex in cat["examples"]:
            typer.echo(f"  • {ex['desc']}")
            typer.echo(f"    {ex['cmd']}\n")
    else:
        typer.echo("\n📚 ModelToolbox 使用示例\n")
        for cat_key, cat in examples.items():
            typer.echo(f"{cat['title']}")
            for ex in cat["examples"]:
                typer.echo(f"  • {ex['desc']}")
                typer.echo(f"    {ex['cmd']}")
            typer.echo()

        typer.echo("💡 提示: 使用 'mtb ux examples <category>' 查看特定类别的示例")
        typer.echo(f"可用类别: {', '.join(examples.keys())}\n")


@ux_app.command("quickstart")
def quickstart() -> None:
    """快速入门向导"""
    typer.echo("🚀 ModelToolbox 快速入门\n")

    typer.echo("第 1 步: 初始化配置")
    typer.echo("  mtb ux init\n")

    typer.echo("第 2 步: 检查环境")
    typer.echo("  mtb ux check\n")

    typer.echo("第 3 步: 选择你的第一个任务\n")

    tasks = [
        ("构建文档知识库", "mtb ingest build --source ./docs --output ./vault"),
        ("尝试本地 LLM", "mtb provider chat --message 'Hello' --model llama3.2"),
        ("创建沙箱环境", "mtb office env create demo"),
        ("索引项目代码", "mtb memory index . --include '*.py'"),
    ]

    for i, (desc, cmd) in enumerate(tasks, 1):
        typer.echo(f"  {i}. {desc}")
        typer.echo(f"     {cmd}\n")

    typer.echo("💡 查看更多示例: mtb ux examples")
    typer.echo("📖 完整文档: https://github.com/lbxAOA/ModelToolbox#readme\n")


def register(root: typer.Typer) -> None:
    """注册到主 CLI"""
    root.add_typer(ux_app, name="ux")
