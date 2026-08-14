"""First-party test runner for ModelToolbox Next."""

from __future__ import annotations

import importlib.util
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType


@dataclass(frozen=True)
class TestFailure:
    path: Path
    name: str
    detail: str


def load_module(path: Path) -> ModuleType:
    name = f"mtb_next_test_{path.stem}_{abs(hash(path))}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load test module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def discover(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("test_*.py") if path.is_file())


@dataclass(frozen=True)
class TestSummary:
    modules: int
    tests: int
    failures: tuple[TestFailure, ...]


def run(root: Path) -> TestSummary:
    failures: list[TestFailure] = []
    executed = 0
    for path in discover(root):
        try:
            module = load_module(path)
        except Exception:
            failures.append(TestFailure(path, "<module>", traceback.format_exc()))
            continue
        for name, value in sorted(vars(module).items()):
            if not name.startswith("test_") or not callable(value):
                continue
            try:
                executed += 1
                value()
            except Exception:
                failures.append(TestFailure(path, name, traceback.format_exc()))
    return TestSummary(len(discover(root)), executed, tuple(failures))


def main() -> int:
    workspace = Path(__file__).resolve().parents[2]
    if str(workspace) not in sys.path:
        sys.path.insert(0, str(workspace))
    root = workspace / "tests"
    summary = run(root)
    if not summary.failures:
        print(f"PASS: {summary.tests} test(s) in {summary.modules} module(s)")
        return 0
    for failure in summary.failures:
        print(f"FAIL: {failure.path.relative_to(root)}::{failure.name}")
        print(failure.detail.rstrip())
    print(f"FAIL: {len(summary.failures)} failure(s) across {summary.tests} test(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
