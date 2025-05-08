"""Database context protocol for repository layer.

This module defines the interface for database contexts used throughout the application.
"""

from abc import abstractmethod
from typing import Protocol, TypeVar


T_co = TypeVar("T_co", covariant=True)


class DBContext(Protocol[T_co]):
    """Database context protocol.

    Provides an abstraction over different database access methods,
    allowing repositories to work with any database backend implementation.
    """

    @property
    @abstractmethod
    def manipulator(self) -> T_co:
        """Get database manipulator for interacting with the database.

        The manipulator is the actual database-specific object used to execute
        operations, such as an SQLAlchemy session, asyncpg connection, etc.

        Returns:
            A database-specific manipulator object.

        """
