"""增量 manifest：用源文件的 sha256 判断是否需要重新转换。

存储于 sqlite。记录 (相对路径, sha256, 输出路径, 转换器, 时间)。
"""

from __future__ import annotations

import hashlib
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS converted (
    rel_path     TEXT PRIMARY KEY,
    sha256       TEXT NOT NULL,
    output_path  TEXT NOT NULL,
    converter    TEXT NOT NULL,
    converted_at TEXT NOT NULL
);
"""


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    """流式计算文件 sha256，避免大文件占内存。"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


class Manifest:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        with closing(self._conn.cursor()) as cur:
            cur.executescript(_SCHEMA)
        self._conn.commit()

    def needs_convert(self, rel_path: str, sha256: str) -> bool:
        """源文件是新的或内容已变 → 需要转换。"""
        with closing(self._conn.cursor()) as cur:
            cur.execute("SELECT sha256 FROM converted WHERE rel_path = ?", (rel_path,))
            row = cur.fetchone()
        return row is None or row[0] != sha256

    def record(self, rel_path: str, sha256: str, output_path: str, converter: str) -> None:
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "INSERT OR REPLACE INTO converted "
                "(rel_path, sha256, output_path, converter, converted_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (rel_path, sha256, output_path, converter, datetime.now(timezone.utc).isoformat()),
            )
        self._conn.commit()

    def all_records(self) -> list[tuple]:
        with closing(self._conn.cursor()) as cur:
            cur.execute("SELECT rel_path, sha256, output_path, converter, converted_at FROM converted")
            return cur.fetchall()

    def remove(self, rel_path: str) -> None:
        with closing(self._conn.cursor()) as cur:
            cur.execute("DELETE FROM converted WHERE rel_path = ?", (rel_path,))
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
