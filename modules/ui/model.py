"""First-party UI view-model contracts shared by presentation clients."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class StateEntry:
    key: str
    value: Any
    value_type: str

    def to_data(self) -> dict[str, Any]:
        return {"key": self.key, "value": self.value, "value_type": self.value_type}


@dataclass(frozen=True)
class WorkbenchSection:
    """A safe, capability-gated placeholder for a future workbench surface."""

    key: str
    title: str
    status: str
    message: str

    def to_data(self) -> dict[str, str]:
        return {
            "key": self.key,
            "title": self.title,
            "status": self.status,
            "message": self.message,
        }


@dataclass(frozen=True)
class WorkbenchShell:
    """Presentation-only shell metadata shared by Flutter and the terminal TUI."""

    sections: tuple[WorkbenchSection, ...]

    def to_data(self) -> dict[str, list[dict[str, str]]]:
        return {"sections": [section.to_data() for section in self.sections]}


@dataclass(frozen=True)
class ViewSnapshot:
    version: str
    state_entries: tuple[StateEntry, ...]
    workbench: WorkbenchShell

    def to_data(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "state_entries": [entry.to_data() for entry in self.state_entries],
            "workbench": self.workbench.to_data(),
        }


def value_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "unknown"


def default_workbench_shell() -> WorkbenchShell:
    return WorkbenchShell(
        sections=(
            WorkbenchSection("session", "Session", "unavailable", "Sessions and streaming are not enabled yet."),
            WorkbenchSection("tools", "Tools", "unavailable", "Tool activity and confirmations are not enabled yet."),
            WorkbenchSection("workspace", "Workspace", "unavailable", "Workspace browsing and search are not enabled yet."),
            WorkbenchSection("settings", "Settings", "unavailable", "Model and runtime settings are not enabled yet."),
        )
    )


def snapshot_from_state(version: str, state: Mapping[str, Any]) -> ViewSnapshot:
    entries = tuple(
        StateEntry(key=key, value=state[key], value_type=value_type(state[key]))
        for key in sorted(state)
    )
    return ViewSnapshot(version=version, state_entries=entries, workbench=default_workbench_shell())
