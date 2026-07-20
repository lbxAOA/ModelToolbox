#!/usr/bin/env python3
"""UserPromptSubmit hook: auto-search the registry for the current task and
inject the best-matching skills as context.

Reads the hook JSON payload from stdin (field `prompt`), searches the skill
registry, and prints a compact `<skill-manager>` block to stdout when there is
a confident match. stdout from a UserPromptSubmit hook is added to the model's
context for that turn.

Always exits 0 — it must never block the user's prompt. On any error it stays
silent.
"""

from __future__ import annotations

import json
import sys

import skilllib

# Don't fire on trivially short prompts or on the manager's own commands.
_MIN_PROMPT_LEN = 8


def _read_prompt() -> str:
    raw = skilllib.read_stdin_utf8()
    if not raw.strip():
        return ""
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return str(data.get("prompt") or data.get("user_prompt") or "")
    except Exception:
        # If it wasn't JSON, treat the raw text as the prompt.
        return raw
    return ""


def main() -> int:
    skilllib.configure_utf8()
    prompt = _read_prompt().strip()
    if len(prompt) < _MIN_PROMPT_LEN:
        return 0
    low = prompt.lstrip().lower()
    if low.startswith("/skill-") or low.startswith("skill-"):
        return 0

    try:
        results = skilllib.search(prompt)
    except Exception:
        return 0

    if not results:
        return 0

    lines = [
        "<skill-manager>",
        "本次任务的候选技能（如适用，请优先用 Skill 工具调用对应技能；不相关可忽略）:",
    ]
    for r in results:
        lines.append(f"- {r['name']}: {skilllib.summarize(r['description'])}  "
                     f"[score {r['score']}]")
    lines.append("</skill-manager>")
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Never block the prompt, whatever happens.
        sys.exit(0)
