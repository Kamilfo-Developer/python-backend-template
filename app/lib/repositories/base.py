"""Base repository abstraction."""

import abc
from typing import Generic, TypeVar

from app.lib.repositories.db_context import DBContext


T = TypeVar("T")


class BaseRepository(abc.ABC, Generic[T]):
    """Base repository interface for data access operations.

    Provides a foundational structure for all repositories in the application,
    ensuring consistent access patterns across different data stores.

    Attributes:
        _db_context: The database context to use for operations

    """

    def __init__(self, db_context: DBContext) -> None:
        """Initialize the repository with a database context.

        Args:
            db_context: The database context to use for operations

        """
        self._db_context = db_context
