"""ingest 阶段清洗结果统计 —— 供 webui 后端展示用。

只读 sqlite manifest（stdlib，无第三方依赖），不 import modelingest 包本身，
避免 Node 后端与 Python 包产生耦合；仅通过子进程调用本脚本。

用法：
    python read_ingest_manifest.py <manifest_sqlite_path>

输出：单行 JSON，字段：
    total / filtered / converted / by_converter / filtered_reasons / near_duplicates / injection_flagged
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "usage: read_ingest_manifest.py <manifest.sqlite>"}))
        return 2
    db_path = Path(sys.argv[1])
    if not db_path.exists():
        print(json.dumps({
            "total": 0, "converted": 0, "filtered": 0,
            "by_converter": {}, "filtered_reasons": {}, "near_duplicates": [],
            "note": "manifest 不存在（尚未运行过 run）",
        }))
        return 0

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute("SELECT rel_path, output_path, converter, converted_at, simhash FROM converted")
        rows = cur.fetchall()
    except sqlite3.Error as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    finally:
        conn.close()

    by_converter: dict[str, int] = {}
    filtered_reasons: dict[str, int] = {}
    filtered_items: list[dict] = []
    converted_items: list[dict] = []
    simhashes: dict[str, int] = {}

    for rel_path, output_path, converter, converted_at, simhash in rows:
        if converter and converter.startswith("filtered:"):
            reason = converter.split(":", 1)[1]
            filtered_reasons[reason] = filtered_reasons.get(reason, 0) + 1
            filtered_items.append({"rel_path": rel_path, "reason": reason, "at": converted_at})
        else:
            by_converter[converter] = by_converter.get(converter, 0) + 1
            converted_items.append({
                "rel_path": rel_path, "output_path": output_path,
                "converter": converter, "at": converted_at,
            })
            if simhash is not None:
                simhashes[rel_path] = simhash

    result = {
        "total": len(rows),
        "converted": len(converted_items),
        "filtered": len(filtered_items),
        "by_converter": by_converter,
        "filtered_reasons": filtered_reasons,
        "filtered_items": filtered_items[:200],
        "converted_items": converted_items[:200],
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
