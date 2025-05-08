"""SQLAlchemy database context implementation.

Provides a concrete implementation of the DBContext protocol for SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.lib.repositories.db_context import DBContext


class SADBContext(DBContext[AsyncSession]):
    """SQLAlchemy database context.

    Wraps an SQLAlchemy AsyncSession to provide a consistent interface
    for repository operations.

    Attributes:
        _async_session: The SQLAlchemy AsyncSession to use for database operations

    """

    def __init__(self, async_session: AsyncSession) -> None:
        """Initialize the SQLAlchemy database context.

        Args:
            async_session: SQLAlchemy async session to use for database operations

        """
        self._async_session = async_session

    @property
    def manipulator(self) -> AsyncSession:
        """Get the SQLAlchemy AsyncSession for database operations.

        Returns:
            The SQLAlchemy AsyncSession instance

        """
        return self._async_session
