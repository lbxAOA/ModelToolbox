"""distill 增量 manifest：记录每个源 md 的 hash + profile，未变则跳过蒸馏。

与阶段 A 的 :class:`modelingest.manifest.Manifest` 分开存储（distill 成本高，需独立增量）。
同时记录该源 md 蒸馏产出的笔记文件列表，便于 clean / 重链。
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS distilled (
    rel_path     TEXT PRIMARY KEY,
    sha256       TEXT NOT NULL,
    profile      TEXT NOT NULL,
    outputs      TEXT NOT NULL,      -- JSON 数组：产出笔记的相对路径
    distilled_at TEXT NOT NULL
);
"""


class DistillManifest:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        with closing(self._conn.cursor()) as cur:
            cur.executescript(_SCHEMA)
        self._conn.commit()

    def needs_distill(self, rel_path: str, sha256: str, profile: str) -> bool:
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "SELECT sha256, profile FROM distilled WHERE rel_path = ?",
                (rel_path,),
            )
            row = cur.fetchone()
        return row is None or row[0] != sha256 or row[1] != profile

    def record(self, rel_path: str, sha256: str, profile: str, outputs: list[str]) -> None:
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "INSERT OR REPLACE INTO distilled "
                "(rel_path, sha256, profile, outputs, distilled_at) VALUES (?, ?, ?, ?, ?)",
                (
                    rel_path,
                    sha256,
                    profile,
                    json.dumps(outputs, ensure_ascii=False),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        self._conn.commit()

    def outputs_of(self, rel_path: str) -> list[str]:
        with closing(self._conn.cursor()) as cur:
            cur.execute("SELECT outputs FROM distilled WHERE rel_path = ?", (rel_path,))
            row = cur.fetchone()
        return json.loads(row[0]) if row else []

    def all_records(self) -> list[tuple]:
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "SELECT rel_path, sha256, profile, outputs, distilled_at FROM distilled"
            )
            return cur.fetchall()

    def remove(self, rel_path: str) -> None:
        with closing(self._conn.cursor()) as cur:
            cur.execute("DELETE FROM distilled WHERE rel_path = ?", (rel_path,))
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
