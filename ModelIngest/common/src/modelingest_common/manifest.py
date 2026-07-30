"""增量处理 Manifest：基于 SHA256 判断文件是否需要重新转换。

从现有 manifest.py 迁移，添加类型注解和文档。
"""

from __future__ import annotations

import hashlib
import sqlite3
from contextlib import closing
from dataclasses import dataclass
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


@dataclass
class ManifestEntry:
    """Manifest 记录条目"""
    rel_path: str
    sha256: str
    output_path: str
    converter: str
    converted_at: str
    simhash: int | None = None


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    """流式计算文件 SHA256 哈希值。
    
    Args:
        path: 文件路径
        chunk_size: 每次读取的块大小（默认 1MB）
    
    Returns:
        SHA256 哈希值（十六进制字符串）
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk_size), b""):
            h.update(block)
    return h.hexdigest()


def _to_signed64(value: int) -> int:
    """SimHash 无符号64位 → SQLite 有符号64位转换"""
    return value - (1 << 64) if value >= (1 << 63) else value


def _to_unsigned64(value: int) -> int:
    """SQLite 有符号64位 → SimHash 无符号64位转换"""
    return value + (1 << 64) if value < 0 else value


class Manifest:
    """增量处理 Manifest 管理器。
    
    记录已转换文件的元信息（路径、哈希、输出位置、转换器、时间戳），
    用于判断文件是否需要重新转换。
    """
    
    def __init__(self, db_path: Path):
        """初始化 Manifest。
        
        Args:
            db_path: SQLite 数据库路径
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        
        # 初始化表结构
        with closing(self._conn.cursor()) as cur:
            cur.executescript(_SCHEMA)
            
            # 向后兼容：旧版本没有 simhash 列
            cur.execute("PRAGMA table_info(converted)")
            cols = {row[1] for row in cur.fetchall()}
            if "simhash" not in cols:
                cur.execute("ALTER TABLE converted ADD COLUMN simhash INTEGER")
        
        self._conn.commit()
    
    def needs_convert(self, rel_path: str, sha256: str) -> bool:
        """判断文件是否需要转换。
        
        Args:
            rel_path: 文件相对路径
            sha256: 文件当前 SHA256 哈希值
        
        Returns:
            True 表示需要转换（文件是新的或内容已变更）
        """
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
        """记录转换完成的文件。
        
        Args:
            rel_path: 源文件相对路径
            sha256: 源文件 SHA256 哈希值
            output_path: 输出文件路径
            converter: 使用的转换器名称
            simhash: 可选的 SimHash 值（用于近似去重）
        """
        stored_hash = _to_signed64(simhash) if simhash is not None else None
        timestamp = datetime.now(timezone.utc).isoformat()
        
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "INSERT OR REPLACE INTO converted "
                "(rel_path, sha256, output_path, converter, converted_at, simhash) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (rel_path, sha256, output_path, converter, timestamp, stored_hash),
            )
        self._conn.commit()
    
    def get_entry(self, rel_path: str) -> ManifestEntry | None:
        """获取指定文件的 Manifest 记录。
        
        Args:
            rel_path: 文件相对路径
        
        Returns:
            ManifestEntry 或 None（未找到）
        """
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "SELECT rel_path, sha256, output_path, converter, converted_at, simhash "
                "FROM converted WHERE rel_path = ?",
                (rel_path,),
            )
            row = cur.fetchone()
        
        if row is None:
            return None
        
        return ManifestEntry(
            rel_path=row[0],
            sha256=row[1],
            output_path=row[2],
            converter=row[3],
            converted_at=row[4],
            simhash=_to_unsigned64(row[5]) if row[5] is not None else None,
        )
    
    def all_records(self) -> list[ManifestEntry]:
        """获取所有已记录的转换条目。
        
        Returns:
            ManifestEntry 列表
        """
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "SELECT rel_path, sha256, output_path, converter, converted_at, simhash "
                "FROM converted"
            )
            rows = cur.fetchall()
        
        return [
            ManifestEntry(
                rel_path=row[0],
                sha256=row[1],
                output_path=row[2],
                converter=row[3],
                converted_at=row[4],
                simhash=_to_unsigned64(row[5]) if row[5] is not None else None,
            )
            for row in rows
        ]
    
    def find_near_duplicate(
        self,
        rel_path: str,
        simhash: int,
        max_distance: int = 3,
    ) -> str | None:
        """查找与指定文件内容相近的已记录文件。
        
        Args:
            rel_path: 当前文件相对路径（会被排除）
            simhash: 当前文件的 SimHash 值
            max_distance: 最大汉明距离（默认 3）
        
        Returns:
            最相近文件的 rel_path，未找到返回 None
        """
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "SELECT rel_path, simhash FROM converted "
                "WHERE simhash IS NOT NULL AND rel_path != ?",
                (rel_path,),
            )
            rows = cur.fetchall()
        
        best_path: str | None = None
        best_distance = max_distance + 1
        
        for other_path, other_hash in rows:
            if other_hash is None:
                continue
            
            # 计算汉明距离
            distance = bin(_to_unsigned64(int(other_hash)) ^ int(simhash)).count("1")
            
            if distance <= max_distance and distance < best_distance:
                best_path = other_path
                best_distance = distance
        
        return best_path
    
    def remove(self, rel_path: str) -> None:
        """删除指定文件的 Manifest 记录。
        
        Args:
            rel_path: 文件相对路径
        """
        with closing(self._conn.cursor()) as cur:
            cur.execute("DELETE FROM converted WHERE rel_path = ?", (rel_path,))
        self._conn.commit()
    
    def close(self) -> None:
        """关闭数据库连接。"""
        self._conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
