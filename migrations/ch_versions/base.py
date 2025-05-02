"""Base ClickHouse migration."""

from abc import ABC

from aiochclient import ChClient


class ClickhouseMigration(ABC):
    """Base class for ClickHouse migration.

    This class provides a framework for managing database schema migrations in ClickHouse.
    Subclasses should implement specific migration logic in the `upgrade` and `downgrade` methods.
    """

    _migrations: list["ClickhouseMigration"] = []

    def __init__(self, version: int) -> None:
        """Initialize a migration instance with a specific version.

        Args:
            version (int): The version number of the migration.

        """
        self.version = version

    def __init_subclass__(cls, version: int) -> None:
        """Initialize a subclass of ClickhouseMigration.

        This method automatically registers the subclass as a migration with the specified version.

        Args:
            version (int): The version number for the subclass migration.

        """
        super().__init_subclass__()
        cls._migrations.append(cls(version))

    @classmethod
    def get_migrations(cls, is_reverse: bool = False) -> list["ClickhouseMigration"]:
        """Get a list of registered migrations, optionally in reverse order.

        Args:
            is_reverse (bool): If True, return the migrations in reverse order.

        Returns:
            list[ClickhouseMigration]: A list of migration instances sorted by version.

        """
        migrations = sorted(cls._migrations, key=lambda obj: obj.version)

        if is_reverse:
            migrations.reverse()

        return migrations

    async def upgrade(self, clickhouse: ChClient) -> None:
        """Perform the upgrade operation for this migration.

        Args:
            clickhouse (ChClient): The ClickHouse client to execute the migration.

        """
        # We set noqa here since we know for sure that there will be no injection in this parameter
        await clickhouse.execute(f"INSERT INTO schema_versions (version) VALUES ({self.version})")  # noqa: S608

    async def downgrade(self, clickhouse: ChClient) -> None:
        """Perform the downgrade operation for this migration.

        Args:
            clickhouse (ChClient): The ClickHouse client to execute the migration.

        """
        # We set noqa here since we know for sure that there will be no injection in this parameter
        await clickhouse.execute(f"DELETE FROM schema_versions WHERE version={self.version}")  # noqa: S608
