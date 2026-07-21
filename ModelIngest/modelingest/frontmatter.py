"""生成 Markdown 顶部的 YAML front-matter，用于溯源。

字段：
- source: 相对于 source_root 的原始文件路径（原件本地保留，不上传）
- sha256: 原始文件内容哈希
- converter: 使用的转换器（markitdown / pymupdf / passthrough ...）
- converted_at: 转换时间（UTC ISO8601）
- assets: 该文档抽取的页图 / 图表相对路径列表（可选）
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable


def _yaml_escape(value: str) -> str:
    if any(c in value for c in ":#[]{}\"'\n") or value.strip() != value:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


def build_frontmatter(
    *,
    source: str,
    sha256: str,
    converter: str,
    assets: Iterable[str] | None = None,
    converted_at: str | None = None,
    near_duplicate_of: str | None = None,
    injection_flagged: int | None = None,
) -> str:
    ts = converted_at or datetime.now(timezone.utc).isoformat()
    lines = ["---"]
    lines.append(f"source: {_yaml_escape(source)}")
    lines.append(f"sha256: {sha256}")
    lines.append(f"converter: {converter}")
    lines.append(f"converted_at: {ts}")
    assets = list(assets or [])
    if assets:
        lines.append("assets:")
        for a in assets:
            lines.append(f"  - {_yaml_escape(a)}")
    if near_duplicate_of:
        lines.append(f"near_duplicate_of: {_yaml_escape(near_duplicate_of)}")
    if injection_flagged:
        lines.append(f"injection_flagged: {injection_flagged}")
    lines.append("generator: ModelIngest")
    lines.append("---")
    return "\n".join(lines) + "\n\n"
