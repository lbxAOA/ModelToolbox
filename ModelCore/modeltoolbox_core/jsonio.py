from __future__ import annotations

import json
import sys
from typing import Any, TextIO


def dump_json(payload: Any, stream: TextIO | None = None, *, pretty: bool = False) -> None:
    """Write a JSON payload without sentinel markers or log parsing hacks."""
    target = stream or sys.stdout
    if pretty:
        json.dump(payload, target, ensure_ascii=False, indent=2, sort_keys=True)
    else:
        json.dump(payload, target, ensure_ascii=False, separators=(",", ":"))
    target.write("\n")
