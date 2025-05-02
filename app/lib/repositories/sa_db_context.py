"""SQLAlchemy database context.."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.lib.repositories.db_context import DBContext


class SADBContext(DBContext[AsyncSession]):
    """Base database context."""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    @property
    def manipulator(self) -> AsyncSession:
        """AsyncSession to use in queries."""
        return self._async_session
