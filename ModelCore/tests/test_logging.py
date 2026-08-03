"""Tests for modeltoolbox_core.logging module."""
import pytest
import logging
from pathlib import Path
from modeltoolbox_core.logging import get_logger, get_log_dir, setup_logging, JSONFormatter


def test_get_log_dir():
    """Test log directory creation."""
    log_dir = get_log_dir()
    assert log_dir.exists()
    assert log_dir.is_dir()
    assert log_dir.name == "logs"


def test_get_logger_basic(clean_loggers):
    """Test basic logger creation."""
    logger = get_logger("test.module")
    assert logger.name == "test.module"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 3


def test_get_logger_custom_level(clean_loggers):
    """Test logger with custom level."""
    logger = get_logger("test.debug", level="DEBUG")
    assert logger.level == logging.DEBUG


def test_get_logger_singleton(clean_loggers):
    """Test that get_logger returns same instance."""
    logger1 = get_logger("test.singleton")
    logger2 = get_logger("test.singleton")
    assert logger1 is logger2


def test_json_formatter():
    """Test JSON log formatting."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    result = formatter.format(record)
    assert '"level": "INFO"' in result
    assert '"message": "Test message"' in result
    assert '"logger": "test"' in result


def test_json_formatter_with_duration():
    """Test JSON formatter with duration."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test",
        args=(),
        exc_info=None
    )
    record.duration_ms = 123.45
    
    result = formatter.format(record)
    assert '"duration_ms": 123.45' in result


def test_setup_logging():
    """Test global logging setup."""
    setup_logging(level="DEBUG")
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG


def test_logger_hierarchy(clean_loggers):
    """Test that child loggers don't propagate."""
    parent = get_logger("parent")
    child = get_logger("parent.child")
    
    assert parent.propagate == False
    assert child.propagate == False
