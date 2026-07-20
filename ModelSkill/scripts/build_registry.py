#!/usr/bin/env python3
"""(Re)build the skill registry: registry/skills-index.json + registry/SKILLS.md.

Usage:
    python scripts/build_registry.py [--quiet]
"""

from __future__ import annotations

import sys

import skilllib


def main(argv: list[str]) -> int:
    skilllib.configure_utf8()
    quiet = "--quiet" in argv or "-q" in argv
    index = skilllib.build_registry()
    if not quiet:
        n = index["skill_count"]
        print(f"Registry rebuilt: {n} skill(s).")
        print(f"  index   -> {skilllib.INDEX_PATH.relative_to(skilllib.PROJECT_ROOT).as_posix()}")
        print(f"  catalog -> {skilllib.CATALOG_PATH.relative_to(skilllib.PROJECT_ROOT).as_posix()}")
        for rec in index["skills"]:
            print(f"  - {rec['name']}  ({len(rec.get('triggers', []))} triggers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
