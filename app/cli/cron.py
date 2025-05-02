"""CRON-related commands."""

from .cli import cli


@cli.group()
def cron() -> None:
    """CRON management commands."""
