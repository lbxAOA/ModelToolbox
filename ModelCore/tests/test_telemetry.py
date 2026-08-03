"""Tests for modeltoolbox_core.telemetry module."""
import pytest
import time
from modeltoolbox_core.telemetry import track_performance, track_errors, record_metric


def test_track_performance_success():
    """Test performance tracking on successful function."""
    @track_performance
    def fast_function():
        return "success"
    
    result = fast_function()
    assert result == "success"


def test_track_performance_with_delay():
    """Test performance tracking with measured delay."""
    @track_performance
    def slow_function():
        time.sleep(0.01)
        return "done"
    
    result = slow_function()
    assert result == "done"


def test_track_performance_with_exception():
    """Test performance tracking when exception raised."""
    @track_performance
    def failing_function():
        raise ValueError("test error")
    
    with pytest.raises(ValueError, match="test error"):
        failing_function()


def test_track_errors_success():
    """Test error tracking on successful function."""
    @track_errors
    def working_function():
        return "ok"
    
    result = working_function()
    assert result == "ok"


def test_track_errors_with_exception():
    """Test error tracking suppresses exception."""
    @track_errors
    def broken_function():
        raise RuntimeError("broken")
    
    result = broken_function()
    assert result is None


def test_record_metric():
    """Test metric recording."""
    record_metric("test_metric", 42.5, "ms")
    record_metric("count", 100)


def test_track_performance_preserves_metadata():
    """Test that decorator preserves function metadata."""
    @track_performance
    def documented_function():
        """This function has docs."""
        pass
    
    assert documented_function.__name__ == "documented_function"
    assert documented_function.__doc__ == "This function has docs."
