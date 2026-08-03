from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from modeltoolbox_core.paths import resolve_in_root

from .envs import OfficeEnv, create_env, get_env, office_root


def create_snapshot(
    name: str,
    snapshot_name: str,
    *,
    project_root: Path | None = None,
) -> dict[str, object]:
    env = create_env(name, project_root=project_root)
    target = _snapshot_dir(name, snapshot_name, project_root=project_root)
    if target.exists():
        raise ValueError(f"Snapshot already exists: {snapshot_name}")
    target.mkdir(parents=True)
    shutil.copytree(env.workspace, target / "workspace")
    manifest = _manifest(env, snapshot_name=snapshot_name)
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def restore_snapshot(
    name: str,
    snapshot_name: str,
    *,
    project_root: Path | None = None,
) -> dict[str, object]:
    env = get_env(name, project_root=project_root)
    source = _snapshot_dir(name, snapshot_name, project_root=project_root) / "workspace"
    if not source.exists():
        raise FileNotFoundError(f"Snapshot does not exist: {snapshot_name}")
    env.root.mkdir(parents=True, exist_ok=True)
    if env.workspace.exists():
        shutil.rmtree(env.workspace)
    shutil.copytree(source, env.workspace)
    return _manifest(env, snapshot_name=snapshot_name)


def list_snapshots(name: str, *, project_root: Path | None = None) -> list[str]:
    root = office_root(project_root) / "snapshots" / name
    if not root.exists():
        return []
    return sorted(path.name for path in root.iterdir() if path.is_dir())


def _snapshot_dir(name: str, snapshot_name: str, *, project_root: Path | None = None) -> Path:
    root = office_root(project_root) / "snapshots"
    return resolve_in_root(root, Path(name) / snapshot_name)


def _manifest(env: OfficeEnv, *, snapshot_name: str) -> dict[str, object]:
    files: list[dict[str, str | int]] = []
    if env.workspace.exists():
        for path in sorted(item for item in env.workspace.rglob("*") if item.is_file()):
            files.append(
                {
                    "path": str(path.relative_to(env.workspace)).replace("\\", "/"),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256(path),
                }
            )
    return {"env": env.name, "snapshot": snapshot_name, "files": files}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()