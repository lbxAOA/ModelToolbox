#!/usr/bin/env python3
"""PostToolUse hook: rebuild the registry when a SKILL.md is created or edited.

Reads the hook JSON payload from stdin and, if the affected file path ends with
SKILL.md (or lives under skills/), silently rebuilds registry/skills-index.json
so newly added/edited skills become searchable mid-session.

Always exits 0 and stays silent on success/no-op.
"""

from __future__ import annotations

import json
import sys

import skilllib


def _affected_paths(data: dict) -> list[str]:
    paths: list[str] = []
    ti = data.get("tool_input") or {}
    for key in ("file_path", "path", "notebook_path"):
        v = ti.get(key)
        if isinstance(v, str):
            paths.append(v)
    return paths


def main() -> int:
    try:
        raw = skilllib.read_stdin_utf8()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0
    if not isinstance(data, dict):
        return 0

    paths = _affected_paths(data)
    touched_skill = any(
        p.replace("\\", "/").lower().endswith("skill.md")
        or "/skills/" in p.replace("\\", "/").lower()
        for p in paths
    )
    if not touched_skill:
        return 0

    try:
        skilllib.build_registry()
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
