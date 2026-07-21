"""命令行入口：modelprovider list / models / ask / ping。"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

from . import config
from .client import LLMClient
from .config import ROLE_DEFAULTS, ROLE_ENV, SPECS


def _cmd_list(args: argparse.Namespace) -> int:
    config.load_dotenv()
    import os

    if getattr(args, "json", False):
        providers = []
        for name, spec in SPECS.items():
            key = os.environ.get(spec.key_env)
            ok = bool(key) or not spec.requires_key
            providers.append({
                "name": name,
                "status": "ok" if ok else "missing_key",
                "default_model": spec.default_model,
                "base_url": os.environ.get(spec.base_env, spec.default_base),
            })
        roles = {
            role: os.environ.get(env, ROLE_DEFAULTS[role])
            for role, env in ROLE_ENV.items()
        }
        print(json.dumps({"providers": providers, "roles": roles}, ensure_ascii=False))
        return 0

    print("Providers:")
    for name, spec in SPECS.items():
        key = os.environ.get(spec.key_env)
        status = "ok" if (key or not spec.requires_key) else "缺少 key"
        base = os.environ.get(spec.base_env, spec.default_base)
        print(f"  - {name:10s} model={spec.default_model:28s} [{status}] {base}")
    print("\nRoles (可用环境变量覆盖):")
    for role, env in ROLE_ENV.items():
        val = os.environ.get(env, ROLE_DEFAULTS[role])
        print(f"  - {role:9s} -> {val}   (env: {env})")
    return 0


def _ollama_root(base_url: str) -> str:
    """OLLAMA_BASE_URL 默认是 openai 兼容路径 .../v1，原生 /api/tags 不带这个后缀。"""
    root = base_url.rstrip("/")
    if root.endswith("/v1"):
        root = root[: -len("/v1")]
    return root


def _cmd_models(args: argparse.Namespace) -> int:
    config.load_dotenv()
    import os

    if args.provider != "ollama":
        print("目前仅支持列出 ollama 已安装模型（--provider ollama）", file=sys.stderr)
        return 2

    spec = SPECS["ollama"]
    base = os.environ.get(spec.base_env, spec.default_base)
    url = f"{_ollama_root(base)}/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        print(f"✗ 无法连接 Ollama（{url}）：{exc}", file=sys.stderr)
        return 1

    names = [
        m.get("name") or m.get("model")
        for m in (data.get("models") or [])
        if isinstance(m, dict)
    ]
    names = [n for n in names if n]

    if args.json:
        print(json.dumps(names, ensure_ascii=False))
        return 0
    print(f"已安装 {len(names)} 个 Ollama 模型：")
    for n in names:
        print(f"  - {n}")
    return 0


def _resolve_client(args: argparse.Namespace) -> LLMClient:
    if args.role:
        return LLMClient.for_role(args.role)
    return LLMClient.for_provider(args.provider, args.model)


def _cmd_ask(args: argparse.Namespace) -> int:
    prompt = args.prompt if args.prompt is not None else sys.stdin.read()
    client = _resolve_client(args)
    text = client.ask(
        prompt, system=args.system, temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    print(text)
    return 0


def _cmd_ping(args: argparse.Namespace) -> int:
    client = _resolve_client(args)
    try:
        client.ping()
    except Exception as exc:  # noqa: BLE001
        print(f"[{client.name}] 失败: {exc}", file=sys.stderr)
        return 1
    print(f"[{client.name}] ok")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="modelprovider",
        description="ModelToolbox 统一大模型调用层",
    )
    sub = p.add_subparsers(dest="command", required=True)

    lst = sub.add_parser("list", help="列出 provider / 角色与配置状态")
    lst.add_argument("--json", action="store_true", help="机读 JSON 输出（供前端解析）")
    lst.set_defaults(func=_cmd_list)

    md = sub.add_parser("models", help="列出某个 provider 当前可用的具体模型（目前仅 ollama）")
    md.add_argument("--provider", default="ollama", help="provider 名（目前仅支持 ollama）")
    md.add_argument("--json", action="store_true", help="机读 JSON 输出（供前端解析）")
    md.set_defaults(func=_cmd_models)

    def add_target(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--provider", default="ollama", help="provider 名")
        sp.add_argument("--model", default=None, help="覆盖默认模型")
        sp.add_argument(
            "--role", default=None, help="按角色调用(teacher/fallback/runner)"
        )

    ask = sub.add_parser("ask", help="发一条 prompt 并打印回答")
    add_target(ask)
    ask.add_argument("prompt", nargs="?", default=None, help="prompt(缺省读 stdin)")
    ask.add_argument("--system", default=None)
    ask.add_argument("--temperature", type=float, default=0.7)
    ask.add_argument("--max-tokens", type=int, default=None, dest="max_tokens")
    ask.set_defaults(func=_cmd_ask)

    ping = sub.add_parser("ping", help="连通性检查")
    add_target(ping)
    ping.set_defaults(func=_cmd_ping)
    return p


def main(argv: "list[str] | None" = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
