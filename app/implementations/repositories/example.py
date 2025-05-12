"""Example repository implementation."""

from app.core.entities.example import Example
from app.core.exceptions.example import NoSuchExample
from app.core.repositories.example import ExampleRepository
from app.lib.repositories.base import BaseRepository
from app.lib.repositories.db_context import DBContext
from app.lib.utils.multisort import multisorted
from app.lib.utils.specification import BaseSpecification, OrderBySpecification
from app.types import ExampleId


class InMemoryExampleRepository(BaseRepository, ExampleRepository):
    """In-memory example repository implementation."""

    def __init__(self, db_context: DBContext[dict[ExampleId, Example]]) -> None:
        """Initialize example repository.

        Args:
            db_context (DBContext[dict[ExampleId, Example]]): Database context.

        """
        self.db_context = db_context

    async def get_example(self, example_id: ExampleId) -> Example:
        """Get example.

        Returns:
            Example: Example entity.

        """
        if not (example := self.db_context.manipulator.get(example_id)):
            raise NoSuchExample

        return example

    async def create_example(self, example: Example) -> None:
        """Create example.

        Args:
            example (Example): Example entity.

        """
        self.db_context.manipulator[example.id] = example

    async def update_example(self, example: Example) -> None:
        """Update example.

        Args:
            example (Example): Example entity.

        """
        self.db_context.manipulator[example.id] = example

    async def delete_example(self, example: Example) -> None:
        """Delete example.

        Args:
            example (Example): Example entity.

        """
        del self.db_context.manipulator[example.id]

    async def get_examples(
        self,
        specifications: list[BaseSpecification] | None = None,
        order_by_specifications: list[OrderBySpecification] | None = None,
    ) -> list[Example]:
        """Get examples.

        Returns:
            list[Example]: List of examples.

        """

        if specifications is None:
            result = list(self.db_context.manipulator.values())
        else:
            result = [
                example
                for example in self.db_context.manipulator.values()
                if all(specification.is_satisfied_by(example) for specification in specifications)
            ]

        if order_by_specifications is not None:
            result = multisorted(result, order_by_specifications)

        return result
