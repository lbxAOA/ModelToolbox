#!/usr/bin/env python3
"""Scaffold a new skill: skills/<name>/SKILL.md from a template, then rebuild
the registry so it is immediately discoverable.

Usage:
    python scripts/new_skill.py --name pdf-extract \
        --description "Extract text and tables from PDF files." \
        --triggers "extract pdf, parse pdf, pdf to text" \
        --tools "Read, Bash"

--name is required. --description/--triggers/--tools are optional but
recommended (they power auto-matching). Refuses to overwrite an existing skill
unless --force is given.
"""

from __future__ import annotations

import argparse
import re
import sys

import skilllib

_TEMPLATE = """---
name: {name}
description: "{description}{trigger_clause}"
allowed-tools: {tools}
---

# {name}

{summary}

## When to use

Describe the situations where this skill applies. Keep it specific so the skill
manager (and Claude) can match tasks to it confidently.

## Steps

1. ...
2. ...
3. ...

## Notes

- Edit this file, then run `/skill-sync` (or just save — the PostToolUse hook
  rebuilds the registry automatically).
"""


def _slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9-]+", "-", name.strip().lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)


def main(argv: list[str]) -> int:
    skilllib.configure_utf8()
    ap = argparse.ArgumentParser(description="Scaffold a new Claude Code skill.")
    ap.add_argument("--name", required=True, help="skill name (kebab-case)")
    ap.add_argument("--description", default="", help="one-line description")
    ap.add_argument("--triggers", default="",
                    help="comma-separated trigger phrases")
    ap.add_argument("--tools", default="Read, Grep, Glob, Bash",
                    help="comma-separated allowed-tools")
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing skill")
    args = ap.parse_args(argv)

    name = _slug(args.name)
    if not name:
        print("error: --name produced an empty slug", file=sys.stderr)
        return 2

    skill_dir = skilllib.SKILLS_DIR / name
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists() and not args.force:
        print(f"error: {skill_md} already exists (use --force to overwrite)",
              file=sys.stderr)
        return 1

    description = args.description.strip() or f"TODO: describe the {name} skill."
    triggers = [t.strip() for t in re.split(r"[,，、]", args.triggers) if t.strip()]
    trigger_clause = ""
    if triggers:
        trigger_clause = " Triggers on: " + ", ".join(triggers) + "."
    tools = ", ".join(t.strip() for t in args.tools.split(",") if t.strip())
    summary = description if description.endswith(".") else description + "."

    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_md.write_text(
        _TEMPLATE.format(
            name=name,
            description=description.rstrip("."),
            trigger_clause=trigger_clause,
            tools=tools,
            summary=summary,
        ),
        encoding="utf-8",
    )

    index = skilllib.build_registry()
    rel = skill_md.relative_to(skilllib.PROJECT_ROOT).as_posix()
    print(f"Created skill '{name}' -> {rel}")
    print(f"Registry rebuilt: {index['skill_count']} skill(s).")
    if not args.description:
        print("Tip: fill in the description + triggers, then run /skill-sync.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
