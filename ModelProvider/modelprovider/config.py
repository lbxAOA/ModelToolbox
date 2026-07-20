"""配置与 provider 规格表。

- 从环境变量（可选 .env）读取 API key、base_url、默认模型。
- 每个 provider 有一份默认规格（base_url / key 环境变量名 / 默认模型），
  用户可用环境变量覆盖。
- 三个"角色"（teacher / fallback / runner）各绑定一个默认 provider:model，
  也可用 MODELTOOLBOX_* 环境变量覆盖。
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def load_dotenv(path: Optional[Path] = None) -> None:
    """把 .env 里的键值加载进 os.environ（不覆盖已存在的变量）。

    极简解析：忽略空行/注释，支持可选 KEY=VALUE 和引号。
    找不到文件则静默跳过。
    """
    candidates = []
    if path is not None:
        candidates.append(Path(path))
    else:
        here = Path.cwd()
        candidates.append(here / ".env")
        # 也尝试模块所在仓库根
        candidates.append(Path(__file__).resolve().parents[2] / ".env")
    for env_path in candidates:
        if not env_path.is_file():
            continue
        for line in env_path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val
        break


@dataclass(frozen=True)
class ProviderSpec:
    """一个 provider 的静态规格。"""

    name: str
    kind: str  # "openai_compat" | "anthropic" | "gemini"
    key_env: str  # 存放 API key 的环境变量名
    base_env: str  # 覆盖 base_url 的环境变量名
    default_base: str
    default_model: str
    requires_key: bool = True


# 内置 provider 规格。OpenAI / DeepSeek / Ollama 共用 OpenAI 兼容协议。
SPECS: dict[str, ProviderSpec] = {
    "openai": ProviderSpec(
        name="openai",
        kind="openai_compat",
        key_env="OPENAI_API_KEY",
        base_env="OPENAI_BASE_URL",
        default_base="https://api.openai.com/v1",
        default_model="gpt-4o-mini",
    ),
    "deepseek": ProviderSpec(
        name="deepseek",
        kind="openai_compat",
        key_env="DEEPSEEK_API_KEY",
        base_env="DEEPSEEK_BASE_URL",
        default_base="https://api.deepseek.com/v1",
        default_model="deepseek-chat",
    ),
    "anthropic": ProviderSpec(
        name="anthropic",
        kind="anthropic",
        key_env="ANTHROPIC_API_KEY",
        base_env="ANTHROPIC_BASE_URL",
        default_base="https://api.anthropic.com/v1",
        default_model="claude-3-5-sonnet-latest",
    ),
    "gemini": ProviderSpec(
        name="gemini",
        kind="gemini",
        key_env="GEMINI_API_KEY",
        base_env="GEMINI_BASE_URL",
        default_base="https://generativelanguage.googleapis.com/v1beta",
        default_model="gemini-1.5-flash",
    ),
    "ollama": ProviderSpec(
        name="ollama",
        kind="openai_compat",
        key_env="OLLAMA_API_KEY",  # 本地一般不需要
        base_env="OLLAMA_BASE_URL",
        default_base="http://localhost:11434/v1",
        default_model="llama3.1",
        requires_key=False,
    ),
}


@dataclass
class ResolvedConfig:
    """某个 provider 解析后的可用配置。"""

    spec: ProviderSpec
    api_key: Optional[str]
    base_url: str
    model: str


def resolve(provider: str, model: Optional[str] = None) -> ResolvedConfig:
    if provider not in SPECS:
        raise KeyError(
            f"未知 provider: {provider!r}. 可选: {', '.join(SPECS)}"
        )
    spec = SPECS[provider]
    api_key = os.environ.get(spec.key_env)
    base_url = os.environ.get(spec.base_env, spec.default_base).rstrip("/")
    chosen_model = model or os.environ.get(
        f"{provider.upper()}_MODEL", spec.default_model
    )
    if spec.requires_key and not api_key:
        raise RuntimeError(
            f"provider {provider!r} 需要 API key，请设置环境变量 {spec.key_env}"
        )
    return ResolvedConfig(spec=spec, api_key=api_key, base_url=base_url, model=chosen_model)


# 三个角色 -> 默认 provider:model（可用环境变量覆盖）。
ROLE_ENV = {
    "teacher": "MODELTOOLBOX_TEACHER",   # 数据蒸馏老师（合成训练样本）
    "fallback": "MODELTOOLBOX_FALLBACK",  # 兜底/对比旗舰
    "runner": "MODELTOOLBOX_RUNNER",     # 训练前先跑通的本地模型
}
ROLE_DEFAULTS = {
    "teacher": "anthropic:claude-3-5-sonnet-latest",
    "fallback": "openai:gpt-4o-mini",
    "runner": "ollama:llama3.1",
}


def resolve_role(role: str) -> ResolvedConfig:
    if role not in ROLE_ENV:
        raise KeyError(f"未知角色: {role!r}. 可选: {', '.join(ROLE_ENV)}")
    spec_str = os.environ.get(ROLE_ENV[role], ROLE_DEFAULTS[role])
    provider, _, model = spec_str.partition(":")
    return resolve(provider.strip(), model.strip() or None)
