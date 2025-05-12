"""Example router."""

from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter
from pyfa_converter_v2 import QueryDepends

from app.schemas.example import ExampleCreateSchema, ExampleFilterSchema, ExampleSchema, ExampleUpdateSchema
from app.services.example import ExampleService
from app.types import ExampleId


example_router = APIRouter(prefix="/examples", tags=["examples"])


@example_router.get("/{example_id}")
@inject
async def get_example(
    example_id: ExampleId,
    example_service: FromDishka[ExampleService],
) -> ExampleSchema:
    """Get example."""
    return await example_service.get_example(example_id)


@example_router.post("/")
@inject
async def create_example(
    create_example: ExampleCreateSchema,
    example_service: FromDishka[ExampleService],
) -> ExampleSchema:
    """Create example."""
    return await example_service.create_example(create_example)


@example_router.put("/{example_id}")
@inject
async def update_example(
    example_id: ExampleId,
    update_example: ExampleUpdateSchema,
    example_service: FromDishka[ExampleService],
) -> ExampleSchema:
    """Update example."""
    return await example_service.update_example(example_id, update_example)


@example_router.delete("/{example_id}", status_code=204)
@inject
async def delete_example(
    example_id: ExampleId,
    example_service: FromDishka[ExampleService],
) -> None:
    """Delete example."""
    await example_service.delete_example(example_id)


@example_router.get("/")
@inject
async def get_examples(
    example_service: FromDishka[ExampleService],
    example_filter: Annotated[ExampleFilterSchema | None, QueryDepends(model_type=ExampleFilterSchema)],
) -> list[ExampleSchema]:
    """Get examples."""
    return await example_service.get_examples(example_filter)
