"""Clickhouse-related commands."""

from contextlib import asynccontextmanager

from aiochclient import ChClient

from app.core.config import AppConfig
from app.lib.dependencies.constructors import clickhouse_client

from .ch_versions import ClickhouseMigration


async def get_version(clickhouse: ChClient) -> int:
    """Retrieve the current schema version from the ClickHouse database.

    This function ensures the `schema_versions` table exists and queries the latest version.

    Args:
        clickhouse (ChClient): The ClickHouse client to execute the query.

    Returns:
        int: The latest schema version number, or 0 if no versions are recorded.

    """
    # Create the schema_versions table if it doesn't exist
    await clickhouse.execute(
        """CREATE TABLE IF NOT EXISTS schema_versions (
                version UInt16
            ) ENGINE = MergeTree()
            ORDER BY version
        """,
    )
    # Query the latest version from the schema_versions table
    result = await clickhouse.fetch("SELECT MAX(version) FROM schema_versions")
    # Extract the version number from the result
    return result[0][0] if result[0][0] is not None else 0


async def migrate(config: AppConfig) -> None:
    """Perform a full migration to the latest schema version.

    This function applies all pending migrations in order.

    Args:
        config (AppConfig): The application configuration containing ClickHouse settings.

    """
    async with asynccontextmanager(clickhouse_client)(config.clickhouse) as ch:
        current_version = await get_version(ch)
        for migration in ClickhouseMigration.get_migrations():
            if current_version >= migration.version:
                continue
            await migration.upgrade(ch)
            current_version = migration.version


async def upgrade(config: AppConfig) -> None:
    """Upgrade the schema to the next version.

    This function applies the next pending migration.

    Args:
        config (AppConfig): The application configuration containing ClickHouse settings.

    """
    async with asynccontextmanager(clickhouse_client)(config.clickhouse) as ch:
        current_version = await get_version(ch)
        for migration in ClickhouseMigration.get_migrations():
            if current_version + 1 == migration.version:
                await migration.upgrade(ch)
                break


async def downgrade(config: AppConfig) -> None:
    """Downgrade the schema to the previous version.

    This function reverts the most recent migration.

    Args:
        config (AppConfig): The application configuration containing ClickHouse settings.

    """
    async with asynccontextmanager(clickhouse_client)(config.clickhouse) as ch:
        current_version = await get_version(ch)
        for migration in ClickhouseMigration.get_migrations(is_reverse=True):
            if current_version == migration.version:
                await migration.downgrade(ch)
                break
