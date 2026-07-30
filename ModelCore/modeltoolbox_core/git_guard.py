from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitDeletionReport:
    deleted_count: int
    deleted_paths: tuple[str, ...]
    max_deleted: int

    @property
    def allowed(self) -> bool:
        return self.deleted_count <= self.max_deleted


def inspect_git_deletions(repo: Path, max_deleted: int = 5) -> GitDeletionReport:
    result = subprocess.run(
        ["git", "status", "--porcelain", "-uall"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    deleted_paths = tuple(_parse_deleted_paths(result.stdout.splitlines()))
    return GitDeletionReport(
        deleted_count=len(deleted_paths), deleted_paths=deleted_paths, max_deleted=max_deleted
    )


def _parse_deleted_paths(lines: list[str]) -> list[str]:
    deleted: list[str] = []
    for line in lines:
        if len(line) < 4:
            continue
        status = line[:2]
        if "D" in status:
            deleted.append(line[3:].strip())
    return deleted
