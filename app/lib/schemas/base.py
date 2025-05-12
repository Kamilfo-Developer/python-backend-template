"""Abstract base classes for schemas."""

from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any, Self

from pydantic import BaseModel, ConfigDict

from app.lib.utils.specification import BaseSpecification, OrderBySpecification


class BaseSchema(BaseModel, ABC):
    """Base schema."""

    model_config = ConfigDict(from_attributes=True)

    def iterate_set_fields(self, exclude: list[str] | None = None) -> Generator[tuple[str, Any], None, None]:
        """Iterate over set fields."""
        if exclude is None:
            exclude = []

        for field_name in self.model_fields_set:
            if field_name in exclude:
                continue
            attr = getattr(self, field_name)
            yield field_name, attr


class BaseEntitySchema[T](BaseSchema):
    """Base entity schema."""

    id: Any

    @abstractmethod
    def to_entity(self) -> T:
        """Convert schema to entity."""

    @classmethod
    @abstractmethod
    def from_entity(cls, entity: T) -> Self:
        """Convert entity to schema."""


class BaseEntityCreateSchema[T](BaseSchema):
    """Base entity create schema."""


class BaseEntityUpdateSchema[T](BaseSchema):
    """Base entity update schema."""

    @abstractmethod
    def update_entity(self, entity: T) -> T:
        """Update entity."""


class BaseFilterSchema(BaseSchema):
    """Base filter schema."""

    @abstractmethod
    def to_specifications(self) -> list[BaseSpecification]:
        """Convert schema to specifications."""

    @abstractmethod
    def to_order_by_specifications(self) -> list[OrderBySpecification]:
        """Convert schema to order by specifications."""
