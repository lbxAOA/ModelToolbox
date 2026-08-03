"""Unified logging system for ModelToolbox.

Provides zero-configuration structured logging with console and file outputs.
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Format log records as JSON Lines."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        if hasattr(record, "command"):
            log_data["command"] = record.command
        
        return json.dumps(log_data, ensure_ascii=False)


def get_log_dir() -> Path:
    """Get or create the logs directory."""
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Local" / "modeltoolbox"
    else:
        base = Path.home() / ".modeltoolbox"
    
    log_dir = base / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        level: Optional log level override (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    log_level = getattr(logging, level.upper()) if level else logging.INFO
    logger.setLevel(log_level)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(levelname)s: %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    log_dir = get_log_dir()
    today = datetime.now().strftime("%Y-%m-%d")
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / f"modeltoolbox-{today}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / f"errors-{today}.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    logger.addHandler(error_handler)
    
    logger.propagate = False
    
    return logger


def setup_logging(level: str = "INFO", module: Optional[str] = None) -> None:
    """Setup global logging configuration.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        module: Optional module name to configure specific logger
    """
    if module:
        get_logger(module, level)
    else:
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
