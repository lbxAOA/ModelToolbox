"""Audit logging for sandbox executions."""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from modeltoolbox_core.config import default_config


@dataclass
class AuditRecord:
    """Single audit log entry."""
    
    timestamp: str
    env: str
    command: list[str]
    cwd: str
    exit_code: int
    duration_ms: int
    stdout_length: int
    stderr_length: int
    network_allowed: bool
    timeout_seconds: float


def audit_log_path(project_root: Path | None = None) -> Path:
    """Get path to audit log file."""
    from .envs import office_root
    
    log_dir = office_root(project_root) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "audit.jsonl"


def write_audit_record(
    env_name: str,
    command: list[str],
    cwd: Path,
    exit_code: int,
    duration_ms: int,
    stdout: str,
    stderr: str,
    network_allowed: bool,
    timeout: float,
    *,
    project_root: Path | None = None,
) -> None:
    """Write an audit record to the log.
    
    Args:
        env_name: Environment name
        command: Command that was executed
        cwd: Working directory
        exit_code: Process exit code
        duration_ms: Execution duration in milliseconds
        stdout: Standard output
        stderr: Standard error
        network_allowed: Whether network was enabled
        timeout: Timeout setting
        project_root: Optional project root
    """
    record = AuditRecord(
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        env=env_name,
        command=list(command),
        cwd=str(cwd),
        exit_code=exit_code,
        duration_ms=duration_ms,
        stdout_length=len(stdout),
        stderr_length=len(stderr),
        network_allowed=network_allowed,
        timeout_seconds=timeout,
    )
    
    log_file = audit_log_path(project_root)
    
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record), ensure_ascii=False))
        f.write("\n")


def read_audit_records(
    *,
    project_root: Path | None = None,
    limit: int | None = None,
) -> list[AuditRecord]:
    """Read audit records from the log.
    
    Args:
        project_root: Optional project root
        limit: Maximum number of records to return (most recent first)
        
    Returns:
        List of audit records
    """
    log_file = audit_log_path(project_root)
    
    if not log_file.exists():
        return []
    
    records: list[AuditRecord] = []
    
    with log_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                records.append(AuditRecord(**data))
            except (json.JSONDecodeError, TypeError):
                continue
    
    # Return most recent first
    records.reverse()
    
    if limit is not None and limit > 0:
        records = records[:limit]
    
    return records
