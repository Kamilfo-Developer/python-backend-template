"""Example schemas."""

from typing import Self

from pydantic import Field

from app.core.entities.example import Example
from app.lib.enums.filter import OrderByType
from app.lib.schemas.base import BaseEntityCreateSchema, BaseEntitySchema, BaseEntityUpdateSchema, BaseFilterSchema
from app.lib.utils.specification import BaseSpecification, ILikeSpecification, LikeSpecification, OrderBySpecification
from app.types import ExampleId


class ExampleUpdateSchema(BaseEntityUpdateSchema[Example]):
    """Example update schema."""

    example_content: str | None = Field(default=None, description="Example content.")
    example_name: str | None = Field(default=None, description="Example name.")

    def update_entity(self, example: Example) -> Example:
        """Update entity."""
        if self.example_name is not None:
            example.name = self.example_name
        if self.example_content is not None:
            example.content = self.example_content
        return example


class ExampleFilterSchema(BaseFilterSchema):
    """Example filter schema."""

    example_name_like: str | None = Field(default=None, description="Example name like filter.")
    example_content_ilike: str | None = Field(default=None, description="Example content ilike filter.")
    order_by_name: OrderByType | None = Field(default=None, description="Order by name.")

    def to_specifications(self) -> list[BaseSpecification]:
        """Convert schema to specifications."""
        return list(
            filter(
                None,
                [
                    LikeSpecification("name", self.example_name_like) if self.example_name_like else None,
                    ILikeSpecification("content", self.example_content_ilike) if self.example_content_ilike else None,
                ],
            ),
        )

    def to_order_by_specifications(self) -> list[OrderBySpecification]:
        return list(
            filter(
                None,
                [
                    OrderBySpecification("name", self.order_by_name) if self.order_by_name else None,
                ],
            ),
        )


class ExampleCreateSchema(BaseEntityCreateSchema[Example]):
    """Example create schema."""

    example_name: str = Field(description="Example name.")
    example_content: str = Field(description="Example content.")


class ExampleSchema(BaseEntitySchema[Example]):
    """Example schema."""

    id: ExampleId = Field(description="Example ID.")
    example_name: str = Field(description="Example name.")
    example_content: str = Field(description="Example content")

    def to_entity(self) -> Example:
        """Convert schema to entity."""
        return Example(id=self.id, name=self.example_name, content=self.example_content)

    @classmethod
    def from_entity(cls, example: Example) -> Self:
        """Convert entity to schema."""
        return cls(id=example.id, example_name=example.name, example_content=example.content)
