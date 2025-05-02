"""File containing version information."""

from importlib.metadata import version

__version__ = version("app")
__version_tuple__ = tuple(int(x) for x in __version__.split("."))
