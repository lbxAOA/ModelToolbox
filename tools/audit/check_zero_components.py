"""Audit the delivery tree for prohibited third-party component indicators."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ALLOWED_LICENSE_PATH = Path("LICENSE")
ALLOWED_NPM_MANIFEST = Path("tui/package.json")
FORBIDDEN_FILE_NAMES = {
    "copying",
    "notice",
    "third_party.md",
    "third-party.md",
    "requirements.txt",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
    "uv.lock",
    "pubspec.lock",
    ".packages",
}
FORBIDDEN_DIRECTORY_NAMES = {
    ".venv",
    "venv",
    "env",
    "node_modules",
    "vendor",
    "third_party",
    "site-packages",
    ".dart_tool",
}
FORBIDDEN_TEXT = (
    "pip install",
    "npm install",
    "actions/checkout",
    "actions/setup-",
    "github actions",
    "pypi.org",
    "cdn.",
    "import pytest",
    "import typer",
    "import click",
    "import rich",
    "import textual",
    "import fastapi",
    "import pydantic",
    "import httpx",
)
TEXT_SUFFIXES = {".py", ".dart", ".toml", ".json", ".txt", ".yml", ".yaml", ".js", ".mjs", ".cjs", ".css", ".html", ".md", ".cmake", ".cc", ".cpp", ".h", ".swift", ".m", ".mm", ".plist", ".xcconfig", ".xib", ".rc", ".manifest"}
_APPROVED_FLUTTER_RUNNERS = (Path("flutter/windows"), Path("flutter/macos"), Path("flutter/linux"))


def _is_approved_flutter_runner(relative: Path) -> bool:
    return any(relative == root or root in relative.parents for root in _APPROVED_FLUTTER_RUNNERS)


def _audit_flutter_layout(root: Path) -> list[str]:
    flutter = root / "flutter"
    if not flutter.exists():
        return []
    violations: list[str] = []
    for child in flutter.iterdir():
        if child.name in {"windows", "macos", "linux", "lib", "test", "pubspec.yaml", ".gitignore", ".metadata", "analysis_options.yaml"}:
            continue
        violations.append(f"Unexpected Flutter delivery path: {child.relative_to(root)}")
    return violations


def _audit_flutter_manifest(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8")
    violations: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith(("cupertino_icons:", "flutter_lints:", "dependency_overrides:", "plugins:")):
            violations.append(f"Forbidden Flutter dependency marker: {path}")
        if any(marker in stripped for marker in ("hosted:", "git:", "path:")):
            violations.append(f"Forbidden Flutter dependency source: {path}")
    return violations


def _audit_npm_manifest(path: Path) -> list[str]:
    try:
        package = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [f"Invalid npm manifest JSON: {path}"]
    if not isinstance(package, dict):
        return [f"Invalid npm manifest object: {path}"]
    violations: list[str] = []
    for field in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies", "bundledDependencies"):
        if package.get(field):
            violations.append(f"Forbidden npm dependency field {field}: {path}")
    scripts = package.get("scripts", {})
    if not isinstance(scripts, dict):
        violations.append(f"Invalid npm scripts object: {path}")
    elif any("install" in name.lower() or "npm " in str(value).lower() for name, value in scripts.items()):
        violations.append(f"Forbidden npm install hook: {path}")
    return violations


def audit(root: Path) -> list[str]:
    violations: list[str] = _audit_flutter_layout(root)
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        lowered_name = path.name.lower()
        if path.is_dir():
            if lowered_name in FORBIDDEN_DIRECTORY_NAMES or lowered_name in {"__pycache__", "build"}:
                violations.append(f"Forbidden directory: {relative}")
            continue
        if not path.is_file():
            continue
        if "license" in lowered_name and relative != ALLOWED_LICENSE_PATH:
            violations.append(f"Unexpected license file: {relative}")
        if lowered_name in FORBIDDEN_FILE_NAMES:
            violations.append(f"Forbidden dependency or notice file: {relative}")
        if lowered_name == "package.json":
            if relative != ALLOWED_NPM_MANIFEST:
                violations.append(f"Unexpected npm manifest: {relative}")
            else:
                violations.extend(_audit_npm_manifest(path))
        if lowered_name == "pubspec.yaml":
            if relative != Path("flutter") / "pubspec.yaml":
                violations.append(f"Unexpected Flutter manifest: {relative}")
            else:
                violations.extend(_audit_flutter_manifest(path))
        if path.suffix.lower() not in TEXT_SUFFIXES:
            if relative in {Path("flutter/.gitignore"), Path("flutter/.metadata")} or _is_approved_flutter_runner(relative):
                continue
            violations.append(f"Unexpected non-text artifact: {relative}")
            continue
        if path == Path(__file__).resolve():
            continue
        try:
            content = path.read_text(encoding="utf-8").lower()
        except UnicodeDecodeError:
            if _is_approved_flutter_runner(relative):
                continue
            violations.append(f"Unexpected non-text artifact: {relative}")
            continue
        for marker in FORBIDDEN_TEXT:
            if marker in content:
                violations.append(f"Forbidden marker {marker!r}: {relative}")
    return violations


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    violations = audit(root)
    if violations:
        print("ZERO-COMPONENT AUDIT FAILED")
        print("\n".join(violations))
        return 1
    print("ZERO-COMPONENT AUDIT PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
