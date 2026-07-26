from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import re
import sqlite3
import time

from modeltoolbox_core.config import default_config
from modeltoolbox_core.paths import resolve_in_root
from modeltoolbox_core.store import connect_sqlite


DEFAULT_EXTENSIONS = {
    ".cfg",
    ".css",
    ".csv",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".ts",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

SKIP_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".modeltoolbox",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    ".venv",
    "__pycache__",
    "dist",
    "node_modules",
}

MAX_FILE_BYTES = 768 * 1024


@dataclass(frozen=True)
class IndexStats:
    root: Path
    database: Path
    indexed: int
    skipped: int
    failed: int


@dataclass(frozen=True)
class SearchHit:
    path: str
    score: float
    snippet: str


def default_database(root: Path | None = None) -> Path:
    config = default_config(root)
    return config.state_dir / "memory" / "graph.db"


def ensure_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY,
            size INTEGER NOT NULL,
            mtime_ns INTEGER NOT NULL,
            sha256 TEXT NOT NULL,
            indexed_at REAL NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS files_fts
        USING fts5(path UNINDEXED, content)
        """
    )


def iter_text_files(root: Path, extensions: set[str] | None = None) -> tuple[list[Path], int]:
    allowed = extensions or DEFAULT_EXTENSIONS
    files: list[Path] = []
    skipped = 0
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            if path.is_file():
                skipped += 1
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in allowed:
            skipped += 1
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                skipped += 1
                continue
        except OSError:
            skipped += 1
            continue
        files.append(path)
    return files, skipped


def read_text(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def index_directory(
    root: Path | str,
    *,
    database: Path | str | None = None,
    extensions: set[str] | None = None,
) -> IndexStats:
    root_path = Path(root).resolve()
    database_path = Path(database).resolve() if database else default_database()
    connection = connect_sqlite(database_path)
    ensure_schema(connection)

    indexed = 0
    failed = 0
    files, skipped = iter_text_files(root_path, extensions)
    with connection:
        for path in files:
            try:
                content = read_text(path)
                stat = path.stat()
                rel_path = path.relative_to(root_path).as_posix()
                digest = hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest()
                connection.execute(
                    """
                    INSERT INTO files(path, size, mtime_ns, sha256, indexed_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(path) DO UPDATE SET
                        size=excluded.size,
                        mtime_ns=excluded.mtime_ns,
                        sha256=excluded.sha256,
                        indexed_at=excluded.indexed_at
                    """,
                    (rel_path, stat.st_size, stat.st_mtime_ns, digest, time.time()),
                )
                connection.execute("DELETE FROM files_fts WHERE path = ?", (rel_path,))
                connection.execute(
                    "INSERT INTO files_fts(path, content) VALUES (?, ?)",
                    (rel_path, content),
                )
                indexed += 1
            except OSError:
                failed += 1
    connection.close()
    return IndexStats(root=root_path, database=database_path, indexed=indexed, skipped=skipped, failed=failed)


def _match_query(query: str) -> str:
    terms = re.findall(r"[\w./-]+", query, flags=re.UNICODE)
    if not terms:
        return f'"{query.replace(chr(34), "")}"'
    return " OR ".join(f'"{term.replace(chr(34), "")}"' for term in terms)


def search_index(
    query: str,
    *,
    root: Path | str | None = None,
    database: Path | str | None = None,
    limit: int = 10,
) -> list[SearchHit]:
    root_path = Path(root).resolve() if root else Path.cwd().resolve()
    database_path = Path(database).resolve() if database else default_database()
    connection = connect_sqlite(database_path)
    ensure_schema(connection)
    match_query = _match_query(query)
    rows = connection.execute(
        """
        SELECT path, bm25(files_fts) AS score,
               snippet(files_fts, 1, '[', ']', ' ... ', 16) AS snippet
        FROM files_fts
        WHERE files_fts MATCH ?
        ORDER BY score
        LIMIT ?
        """,
        (match_query, limit),
    ).fetchall()
    connection.close()
    return [SearchHit(path=row[0], score=float(row[1]), snippet=row[2]) for row in rows]


def impact_candidates(path: Path | str, *, root: Path | str | None = None, limit: int = 20) -> list[SearchHit]:
    root_path = Path(root).resolve() if root else Path.cwd().resolve()
    target = resolve_in_root(root_path, path)
    terms = {target.name, target.stem}
    if target.suffix:
        terms.add(target.suffix.lstrip("."))
    return search_index(" ".join(sorted(terms)), root=root_path, limit=limit)
