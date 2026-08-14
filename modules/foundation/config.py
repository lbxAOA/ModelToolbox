"""Small JSON configuration contract for ModelToolbox Next."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .errors import ValidationError
from .storage import read_json


@dataclass(frozen=True)
class Config:
    output_format: str = "text"
    log_level: str = "info"


def load_config(
    config_path: Path | None,
    environ: Mapping[str, str],
    overrides: Mapping[str, Any],
) -> Config:
    values: dict[str, Any] = {"output_format": "text", "log_level": "info"}
    if config_path is not None:
        stored = read_json(config_path, {})
        if not isinstance(stored, dict):
            raise ValidationError("invalid-config", "Configuration must be a JSON object.")
        values.update(stored)
    if "MODELTOOLBOX_NEXT_LOG_LEVEL" in environ:
        values["log_level"] = environ["MODELTOOLBOX_NEXT_LOG_LEVEL"]
    values.update(overrides)
    if values.get("output_format") not in {"text", "json"}:
        raise ValidationError("invalid-config", "output_format must be text or json.")
    if values.get("log_level") not in {"error", "warning", "info", "debug"}:
        raise ValidationError("invalid-config", "log_level must be error, warning, info, or debug.")
    return Config(output_format=values["output_format"], log_level=values["log_level"])
