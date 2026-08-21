"""Explicit integration contracts; only verified adapters permit writes."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from modules.foundation.errors import ValidationError


@dataclass(frozen=True)
class IntegrationAdapter:
    id: str
    name: str
    contract_status: str
    write_enabled: bool
    mcp_supported: bool
    skills_supported: bool
    message: str
    config_path: Path | None

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "contract_status": self.contract_status,
            "write_enabled": self.write_enabled,
            "mcp_supported": self.mcp_supported,
            "skills_supported": self.skills_supported,
            "message": self.message,
            "config_status": "missing" if self.config_path is not None and not self.config_path.exists() else "ready" if self.config_path is not None else "export-only",
        }


def integration_adapters(environ: Mapping[str, str] | None = None) -> list[IntegrationAdapter]:
    environment = os.environ if environ is None else environ
    home = Path(environment.get("USERPROFILE") or environment.get("HOME") or Path.home())
    return [
        IntegrationAdapter("claude-code", "Claude Code", "verified", True, True, True, "Claude Code managed configuration is enabled.", home / ".claude" / "settings.json"),
        IntegrationAdapter("cursor", "Cursor", "pending", False, True, True, "Cursor is inspection/export-only until its configuration contract is verified.", None),
        IntegrationAdapter("vscode", "VS Code", "pending", False, True, True, "VS Code is inspection/export-only until its configuration contract is verified.", None),
        IntegrationAdapter("windsurf", "Windsurf", "pending", False, True, True, "Windsurf is inspection/export-only until its configuration contract is verified.", None),
        IntegrationAdapter("codex-cli", "Codex CLI", "pending", False, True, True, "Codex CLI is inspection/export-only until its configuration contract is verified.", None),
        IntegrationAdapter("codex-desktop", "Codex Desktop", "unavailable", False, False, False, "Codex Desktop has no verified configuration contract.", None),
        IntegrationAdapter("generic-export", "Generic export", "export-only", False, True, True, "Generate a reviewed configuration bundle for manual import.", None),
    ]


class IntegrationService:
    def __init__(self, environ: Mapping[str, str] | None = None) -> None:
        self.environ = environ

    def list(self) -> dict[str, Any]:
        return {"adapters": [adapter.summary() for adapter in integration_adapters(self.environ)]}

    def inspect(self, adapter_id: object) -> dict[str, Any]:
        if not isinstance(adapter_id, str):
            raise ValidationError("invalid-adapter", "Integration adapter is invalid.")
        for adapter in integration_adapters(self.environ):
            if adapter.id == adapter_id:
                return adapter.summary()
        raise ValidationError("integration-missing", "Integration adapter was not found.")
