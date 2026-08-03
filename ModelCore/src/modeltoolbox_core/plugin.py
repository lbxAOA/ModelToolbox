from __future__ import annotations

from importlib.metadata import EntryPoint, entry_points
from typing import Callable

import typer


class PluginLoadError(RuntimeError):
    pass


def load_plugins(root: typer.Typer, *, skip_names: set[str] | None = None) -> None:
    for entry_point in _iter_entry_points(skip_names=skip_names):
        register = _load_register(entry_point)
        register(root)


def _iter_entry_points(*, skip_names: set[str] | None = None) -> list[EntryPoint]:
    skipped = {"core"}
    if skip_names:
        skipped.update(skip_names)

    selected = entry_points(group="mtb.plugins")
    return [entry_point for entry_point in selected if entry_point.name not in skipped]


def _load_register(entry_point: EntryPoint) -> Callable[[typer.Typer], None]:
    try:
        loaded = entry_point.load()
    except Exception as exc:  # pragma: no cover - message preserves plugin source.
        raise PluginLoadError(f"Failed to load plugin {entry_point.name}: {exc}") from exc
    if not callable(loaded):
        raise PluginLoadError(f"Plugin {entry_point.name} is not callable")
    return loaded
