"""Example repository."""

from typing import Protocol

from app.core.entities.example import Example
from app.lib.utils.specification import BaseSpecification, OrderBySpecification
from app.types import ExampleId


class ExampleRepository(Protocol):
    """Example repository."""

    async def get_example(self, example_id: ExampleId) -> Example:
        """Get example.

        Raises:
            NoSuchExample.

        Returns:
            Example: Example entity.

        """

    async def create_example(self, example: Example) -> None:
        """Create example.

        Args:
            example (Example): Example entity.

        Returns:
            Example: Example entity.

        """

    async def update_example(self, example: Example) -> None:
        """Update example.

        Args:
            example (Example): Example entity.

        Returns:
            Example: Updated example entity.

        """

    async def delete_example(self, example: Example) -> None:
        """Delete example.

        Args:
            example (Example): Example entity.

        """

    async def get_examples(
        self,
        specifications: list[BaseSpecification] | None = None,
        order_by_specifications: list[OrderBySpecification] | None = None,
    ) -> list[Example]:
        """Get examples which satisfy the specifications' conditions.

        If the list of specificaions is None, all examples will be returned.

        If the list of order_by_specification is None, no ordering will be applied.

        Args:
            specifications (list[BaseSpecification] | None): A list of specifications. Defaults to None.
            order_by_specifications (list[OrderBySpecification] | None): A list of order by specifications.
            Defaults to None.

        Returns:
            list[Example]: A list of examples which satisfy the specifications' conditions.

        """
