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
    converted_at TEXT NOT NULL,
    simhash      INTEGER
);
"""


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    """流式计算文件 sha256，避免大文件占内存。"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def _to_signed64(value: int) -> int:
    """SimHash 是无符号 64 bit，SQLite INTEGER 是有符号 64 bit，存入前要转换，
    否则高位为 1 时会 OverflowError。"""
    return value - (1 << 64) if value >= (1 << 63) else value


def _to_unsigned64(value: int) -> int:
    return value + (1 << 64) if value < 0 else value


class Manifest:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        with closing(self._conn.cursor()) as cur:
            cur.executescript(_SCHEMA)
            # 旧库迁移：早期版本没有 simhash 列。
            cur.execute("PRAGMA table_info(converted)")
            cols = {row[1] for row in cur.fetchall()}
            if "simhash" not in cols:
                cur.execute("ALTER TABLE converted ADD COLUMN simhash INTEGER")
        self._conn.commit()

    def needs_convert(self, rel_path: str, sha256: str) -> bool:
        """源文件是新的或内容已变 → 需要转换。"""
        with closing(self._conn.cursor()) as cur:
            cur.execute("SELECT sha256 FROM converted WHERE rel_path = ?", (rel_path,))
            row = cur.fetchone()
        return row is None or row[0] != sha256

    def record(
        self,
        rel_path: str,
        sha256: str,
        output_path: str,
        converter: str,
        simhash: int | None = None,
    ) -> None:
        stored_hash = _to_signed64(simhash) if simhash is not None else None
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "INSERT OR REPLACE INTO converted "
                "(rel_path, sha256, output_path, converter, converted_at, simhash) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (rel_path, sha256, output_path, converter, datetime.now(timezone.utc).isoformat(), stored_hash),
            )
        self._conn.commit()

    def all_records(self) -> list[tuple]:
        with closing(self._conn.cursor()) as cur:
            cur.execute("SELECT rel_path, sha256, output_path, converter, converted_at FROM converted")
            return cur.fetchall()

    def find_near_duplicate(self, rel_path: str, simhash: int, max_distance: int = 3) -> str | None:
        """在已记录的其它文件中找 simhash 汉明距离 <= max_distance 的最相近者。

        返回该文件的 rel_path，找不到则返回 None。用于跨来源近似去重标记
        （不删除内容，只在 front-matter 里记一笔，交由下游/人工决定取舍）。
        """
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "SELECT rel_path, simhash FROM converted WHERE simhash IS NOT NULL AND rel_path != ?",
                (rel_path,),
            )
            rows = cur.fetchall()
        best: str | None = None
        best_dist = max_distance + 1
        for other_rel, other_hash in rows:
            if other_hash is None:
                continue
            dist = bin(_to_unsigned64(int(other_hash)) ^ int(simhash)).count("1")
            if dist <= max_distance and dist < best_dist:
                best, best_dist = other_rel, dist
        return best

    def remove(self, rel_path: str) -> None:
        with closing(self._conn.cursor()) as cur:
            cur.execute("DELETE FROM converted WHERE rel_path = ?", (rel_path,))
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
