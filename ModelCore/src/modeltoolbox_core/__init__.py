"""Shared runtime primitives for ModelToolbox."""

from importlib.metadata import PackageNotFoundError, version

__all__ = ["__version__"]

try:
    __version__ = version("modeltoolbox-core")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"
