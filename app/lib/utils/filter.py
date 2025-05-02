"""Filtration utilities."""

from logging import getLogger
from typing import Any, TypeVar

from pydantic.fields import FieldInfo
from sqlalchemy import ColumnClause, Select, Text, cast, column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, InstrumentedAttribute, aliased

from app.lib.enums.filter import FilterType, OrderByType
from app.lib.exceptions.filter import FilterGroupAlreadyInUseException
from app.lib.schemas.base import BaseSchema

logger = getLogger(__name__)

_SelectType = TypeVar("_SelectType", bound=Any)


def add_filters_to_query(
    query: Select[_SelectType],
    table: type[DeclarativeBase],
    body: BaseSchema,
    *,
    include_order_by: bool = True,
) -> Select[_SelectType]:
    """Add filter to query.

    Args:
        query (GenerativeSelect): Query to filter.
        table (type[AbstractModel]): Table to filter.
        body (BaseSchema): Schema to filter.
        include_order_by (bool): Include order by filters.

    Returns:
        Select[_SelectType]: Filtered query.

    """
    groups = set[str]()

    for field_name, field in body.model_fields.items():
        field_value = getattr(body, field_name)
        if field_value is None:
            continue

        if callable(field.json_schema_extra):
            logger.warning(
                "Filter schema extra for field %s.%s is not a dict, but a callable",
                body.__class__.__name__,
                field_name,
            )
            continue

        extra = _get_field_extra(field)
        table_column = extra.get("table_column", field_name)
        filter_type = extra.get("filter_type", FilterType.eq)

        _check_filter_group(groups, extra)

        if _should_skip_filter(filter_type, table_column, field_value):
            continue

        table_column_obj = _get_table_column_obj(table, table_column)
        _add_filter_to_query(query, table_column_obj, field_value, filter_type, include_order_by, extra)

    logger.debug("Filtered query: %s", query)
    return query


def _get_field_extra(field: FieldInfo) -> dict[str, Any]:
    if field.json_schema_extra is not None and not callable(field.json_schema_extra):
        return field.json_schema_extra
    if hasattr(field, "_inititial_kwargs"):
        return field._inititial_kwargs
    return {}


def _check_filter_group(groups: set[str], extra: dict[str, Any]) -> None:
    filter_group = extra.get("group")
    if filter_group is not None:
        if filter_group in groups:
            raise FilterGroupAlreadyInUseException(group=filter_group)
        groups.add(filter_group)


def _should_skip_filter(filter_type: FilterType, table_column: str, field_value: Any) -> bool:
    if filter_type == FilterType.skip:
        logger.debug(
            "Skipping filter by %s with %s and %s",
            table_column,
            filter_type,
            field_value,
        )
        return True
    return False


def _get_table_column_obj(
    table: type[DeclarativeBase],
    table_column: str,
) -> InstrumentedAttribute[Any] | ColumnClause[Any]:
    current_model = table
    for col in table_column.split("."):
        table_column_obj: ColumnClause[Any] = getattr(current_model, col, column(table_column))

        if hasattr(table_column_obj, "property") and hasattr(table_column_obj.property, "mapper"):
            current_model = table_column_obj.property.mapper.class_
        else:
            break
    return table_column_obj


def _add_filter_to_query(
    query: Select[_SelectType],
    table_column_obj: InstrumentedAttribute[Any] | ColumnClause[Any],
    field_value: Any,
    filter_type: FilterType,
    include_order_by: bool,
    extra: dict[str, Any],
) -> None:
    match filter_type:
        case FilterType.eq:
            query = query.filter(table_column_obj == field_value)
        case FilterType.ne:
            query = query.filter(table_column_obj != field_value)
        case FilterType.in_list:
            query = query.filter(table_column_obj.in_(field_value))
        case FilterType.not_in_list:
            query = query.filter(table_column_obj.not_in(field_value))
        case FilterType.gt:
            query = query.filter(table_column_obj > field_value)
        case FilterType.ge:
            query = query.filter(table_column_obj >= field_value)
        case FilterType.lt:
            query = query.filter(table_column_obj < field_value)
        case FilterType.le:
            query = query.filter(table_column_obj <= field_value)
        case FilterType.like:
            query = query.filter(table_column_obj.like(field_value))
        case FilterType.ilike:
            query = query.filter(table_column_obj.ilike(field_value))
        case FilterType.order_by:
            if include_order_by:
                query = query.order_by(
                    table_column_obj.asc() if field_value == OrderByType.ASC else table_column_obj.desc(),
                )
        case FilterType.func:
            func = extra.get("filter_func")
            if func is None:
                raise ValueError("Filter function is not defined")
            query = func(query, table_column_obj, field_value)
        case _:
            raise NotImplementedError


def inclusion_filter(
    query: "Select[_SelectType]",
    column: "InstrumentedAttribute[Any]",
    value: bool,
) -> "Select[_SelectType]":
    """Get query with inclusion filter.

    Args:
        query (GenerativeSelect): Query to filter.
        column (InstrumentedAttribute[Any]): Column for filter.
        value (bool): Inclusion type.

    """
    return query.filter(column.is_not(None) if value else column.is_(None))


def translation_filter(
    query: "Select[_SelectType]",
    column: "InstrumentedAttribute[Any]",
    value: str,
) -> "Select[_SelectType]":
    """Translation filter.

    Args:
        query (Select): Query.
        column (InstrumentedAttribute): Column to filter.
        value (str): Value to filter.

    Returns:
        Select: Filtered query.

    """
    TranslationModelInQuery = aliased(column.parent.class_)
    query = query.join(TranslationModelInQuery)
    return query.filter(cast(TranslationModelInQuery.translations, JSONB).cast(Text).ilike(f"%{value}%"))
