"""Clickhouse-related commands."""

from asyncio import run as asyncio_run

from app.core.config import AppConfig
from migrations import clickhouse as ch

from .cli import cli


@cli.group()
def clickhouse() -> None:
    """Clickhouse management commands."""


@clickhouse.command()
def migrate() -> None:
    """Run the clickhouse migrations."""
    config = AppConfig.from_env()
    asyncio_run(ch.migrate(config))


@clickhouse.command()
def upgrade() -> None:
    """Run next clickhouse migration."""
    config = AppConfig.from_env()
    asyncio_run(ch.upgrade(config))


@clickhouse.command()
def downgrade() -> None:
    """Run previous clickhouse migration."""
    config = AppConfig.from_env()
    asyncio_run(ch.downgrade(config))
