#!/usr/bin/env python3
"""Search the skill registry for skills matching a free-text task.

Usage:
    python scripts/search_skills.py "ingest this pdf into my notes"
    python scripts/search_skills.py --json "..."        # machine-readable
    python scripts/search_skills.py --top 5 "..."

Exit code is always 0 (a clean "no match" is not an error).
"""

from __future__ import annotations

import json
import sys

import skilllib


def main(argv: list[str]) -> int:
    skilllib.configure_utf8()
    as_json = False
    top_n = skilllib.DEFAULT_TOP_N
    query_parts: list[str] = []

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--json":
            as_json = True
        elif arg == "--top":
            i += 1
            if i < len(argv):
                try:
                    top_n = int(argv[i])
                except ValueError:
                    pass
        else:
            query_parts.append(arg)
        i += 1

    query = " ".join(query_parts).strip()
    if not query:
        print("usage: search_skills.py [--json] [--top N] \"<task description>\"",
              file=sys.stderr)
        return 0

    index = skilllib.load_index()
    if index is None:
        # Index missing -> build it on demand so first run still works.
        index = skilllib.build_registry()

    results = skilllib.search(query, index=index, top_n=top_n)

    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    if not results:
        print(f'No registered skill clearly matches: "{query}"')
        return 0

    print(f'Matched skills for: "{query}"')
    for n, r in enumerate(results, 1):
        print(f"  {n}. {r['name']}  [score {r['score']}]")
        print(f"     {skilllib.summarize(r['description'])}")
        print(f"     -> {r['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
