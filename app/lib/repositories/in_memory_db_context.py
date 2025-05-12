"""In-memory database context."""

from app.lib.repositories.db_context import DBContext


class InMemoryDBContext[T, P](DBContext[dict[T, P]]):
    """In-memory database context."""

    def __init__(self) -> None:
        """Initialize the in-memory database context."""
        self.db: dict[T, P] = {}

    @property
    def manipulator(self) -> dict[T, P]:
        """Get the manipulator for the in-memory database context."""
        return self.db
