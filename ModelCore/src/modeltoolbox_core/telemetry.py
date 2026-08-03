"""Performance monitoring and telemetry for ModelToolbox.

Provides decorators and utilities for tracking command performance and errors.
"""
import time
import functools
from typing import Callable, Any, TypeVar, cast
from .logging import get_logger

logger = get_logger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def track_performance(func: F) -> F:
    """Decorator to track function execution time.
    
    Logs duration and any exceptions raised.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        func_name = func.__name__
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start) * 1000
            
            log_record = logger.makeRecord(
                logger.name,
                20,
                func.__code__.co_filename,
                func.__code__.co_firstlineno,
                f"{func_name} completed",
                (),
                None
            )
            log_record.duration_ms = duration_ms
            log_record.command = func_name
            logger.handle(log_record)
            
            return result
        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(
                f"{func_name} failed after {duration_ms:.1f}ms: {e}",
                exc_info=True
            )
            raise
    
    return cast(F, wrapper)


def track_errors(func: F) -> F:
    """Decorator to track and log errors without re-raising.
    
    Useful for background tasks or optional operations.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"{func.__name__} encountered error: {e}",
                exc_info=True
            )
            return None
    
    return cast(F, wrapper)


def record_metric(name: str, value: float, unit: str = "") -> None:
    """Record a custom metric.
    
    Args:
        name: Metric name
        value: Metric value
        unit: Optional unit (e.g., "ms", "bytes", "count")
    """
    logger.info(f"Metric: {name}={value}{unit}")
