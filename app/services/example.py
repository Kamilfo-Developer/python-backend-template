"""Example service."""

from app.core.entities.example import Example
from app.core.repositories.example import ExampleRepository
from app.schemas.example import ExampleCreateSchema, ExampleFilterSchema, ExampleSchema, ExampleUpdateSchema
from app.types import ExampleId


class ExampleService:
    """Example service."""

    def __init__(self, example_repository: ExampleRepository) -> None:
        self._example_repository = example_repository

    async def get_example(self, example_id: ExampleId) -> ExampleSchema:
        """Get example."""
        example = await self._example_repository.get_example(example_id)
        return ExampleSchema.from_entity(example)

    async def create_example(self, create_example: ExampleCreateSchema) -> ExampleSchema:
        """Create example."""
        example = Example.create(name=create_example.example_name, content=create_example.example_content)
        await self._example_repository.create_example(example)
        return ExampleSchema.from_entity(example)

    async def update_example(self, example_id: ExampleId, update_example: ExampleUpdateSchema) -> ExampleSchema:
        """Update example."""
        example = await self._example_repository.get_example(example_id)
        example = update_example.update_entity(example)
        await self._example_repository.update_example(example)
        return ExampleSchema.from_entity(example)

    async def delete_example(self, example_id: ExampleId) -> None:
        """Delete example."""
        example = await self._example_repository.get_example(example_id)
        await self._example_repository.delete_example(example)

    async def get_examples(
        self,
        example_filter: ExampleFilterSchema | None,
    ) -> list[ExampleSchema]:
        """Get examples."""
        examples = await self._example_repository.get_examples(
            example_filter.to_specifications() if example_filter else None,
            example_filter.to_order_by_specifications() if example_filter else None,
        )
        return [ExampleSchema.from_entity(example) for example in examples]
