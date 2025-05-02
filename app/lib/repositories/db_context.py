"""Base database context."""

from abc import abstractmethod
from typing import Protocol


class DBContext[T](Protocol):
    """Database context."""

    @property
    @abstractmethod
    def manipulator(self) -> T:
        """Get database manipulator which can be used for controlling the database.

        For example, it could be an SQLAlchemy async session or an asyncpg connection.

        Returns:
            T: Any generic manipulator.
        """
