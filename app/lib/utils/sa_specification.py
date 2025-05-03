"""Module containing utilities."""

from typing import Any, TypeVar

from sqlalchemy import Select, not_, or_
from sqlalchemy.orm import DeclarativeBase, InstrumentedAttribute

from app.lib.enums.filter import OrderByType
from app.lib.utils.rattrs import rgetattr
from app.lib.utils.specification import (
    BaseSpecification,
    EqualsSpecification,
    GreaterThanOrEqualsToSpecification,
    GreaterThanSpecification,
    ILikeSpecification,
    InListSpecification,
    LessThanOrEqualsToSpecification,
    LessThanSpecification,
    LikeSpecification,
    NotEqualsSpecification,
    NotInListSpecification,
    NotSubListSpecification,
    OrderBySpecification,
    SubListSpecification,
)


_SelectType = TypeVar("_SelectType", bound=Any)


# This noqa is here since this function is not really that complex
def add_specifications_to_query(  # noqa: C901 PLR0912
    query: Select[_SelectType],
    table: type[DeclarativeBase],
    specifications: list[BaseSpecification],
) -> Select[_SelectType]:
    """Add specifications to a query.

    Args:
        query (_SelectType): The query to add specifications to.
        table (type[DeclarativeBase]): The table to filter.
        specifications (list[BaseSpecification]): The specifications.

    Returns:
        Select[_SelectType]: The result query.

    """
    for specification in specifications:
        table_column_obj: InstrumentedAttribute = rgetattr(table, specification.field)

        match specification:
            case EqualsSpecification():
                query = query.where(table_column_obj == specification.value)
            case NotEqualsSpecification():
                query = query.where(table_column_obj != specification.value)
            case InListSpecification():
                query = query.where(table_column_obj.in_(specification.value))
            case NotInListSpecification():
                query = query.where(table_column_obj.not_in(specification.value))
            case SubListSpecification():
                query = query.where(or_(*[table_column_obj == value for value in specification.value]))
            case NotSubListSpecification():
                query = query.where(not_(or_(*[table_column_obj == value for value in specification.value])))
            case GreaterThanSpecification():
                query = query.where(table_column_obj > specification.value)
            case GreaterThanOrEqualsToSpecification():
                query = query.where(table_column_obj >= specification.value)
            case LessThanSpecification():
                query = query.where(table_column_obj < specification.value)
            case LessThanOrEqualsToSpecification():
                query = query.where(table_column_obj <= specification.value)
            case LikeSpecification():
                query = query.where(table_column_obj.like(specification.value))
            case ILikeSpecification():
                query = query.where(table_column_obj.ilike(specification.value))
            case OrderBySpecification():
                query = query.order_by(
                    table_column_obj.asc() if specification.value == OrderByType.ASC else table_column_obj.desc(),
                )
            case _:
                raise ValueError("Incorrect specification passed.")

    return query
