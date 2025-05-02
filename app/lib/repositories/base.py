"""Base repository."""

import abc

from app.lib.repositories.db_context import DBContext


class BaseRepository(abc.ABC):
    """Base repository."""

    def __init__(self, db_context: DBContext) -> None:
        self._db_context = db_context
