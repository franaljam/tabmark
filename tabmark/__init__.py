"""tabmark – lightweight browser bookmark exporter."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("tabmark")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
