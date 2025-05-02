"""ClickHouse utilities."""

from enum import StrEnum
from logging import getLogger
from typing import Any, Self

from aiochclient import ChClient
from aiochclient.types import py2ch
from pydantic.fields import FieldInfo

from app.lib.enums.filter import FilterType
from app.lib.schemas.base import BaseSchema

logger = getLogger(__name__)


class QueryType(StrEnum):
    """Query type."""

    INSERT = "insert"
    SELECT = "select"
    UPDATE = "update"
    DELETE = "delete"


def decode_ch_value(value: Any) -> str:
    """Decode clickhouse value."""
    return py2ch(value).decode("utf-8")


class ChQuery:
    """Clickhouse query."""

    def __init__(self, table_name: str):
        """Initializes the query builder with a table name.

        Args:
            table_name (str): The name of the table to query.

        """
        self._table_name = table_name
        self._type: QueryType | None = None
        self.conditions_: list[str] = []
        self.columns_: list[str] = []
        self.values_: list[list[Any]] = []
        self.limit_: int | None = None
        self.offset_: int | None = None
        self.order_by_: list[str] = []
        self.group_by_: list[str] = []
        self.set_values_: dict[str, Any] = {}

    def insert(self, columns: list[str], values: list[list[Any]]) -> Self:
        """Sets up an INSERT query.

        Args:
            columns (list[str]): The columns to insert values into.
            values (list[list[Any]]): The values to insert.

        Returns:
            Self: The current query object.

        """
        self._type = QueryType.INSERT
        self.columns_ = columns
        self.values_ = values
        return self

    def select(self, columns: list[str] | None = None, where: list[str] | None = None) -> Self:
        """Sets up a SELECT query.

        Args:
            columns (list[str], optional): The columns to select. Defaults to all columns.
            where (list[str], optional): Conditions for the WHERE clause.

        Returns:
            Self: The current query object.

        """
        self._type = QueryType.SELECT
        self.columns_ = columns if columns else []
        self.conditions_ = where if where else []
        return self

    def update(self, set_values: dict[str, Any], where: list[str] | None = None) -> Self:
        """Sets up an UPDATE query.

        Args:
            set_values (dict[str, Any]): The column-value pairs to update.
            where (list[str], optional): Conditions for the WHERE clause.

        Returns:
            Self: The current query object.

        """
        self._type = QueryType.UPDATE
        self.set_values_ = set_values
        self.conditions_ = where if where else []
        return self

    def delete(self, where: list[str] | None = None) -> Self:
        """Sets up a DELETE query.

        Args:
            where (list[str], optional): Conditions for the WHERE clause.

        Returns:
            Self: The current query object.

        """
        self._type = QueryType.DELETE
        self.conditions_ = where if where else []
        return self

    def limit(self, value: int | None) -> Self:
        """Adds a LIMIT clause to the query.

        Args:
            value (int | None): The maximum number of records to return.

        Returns:
            Self: The current query object.

        """
        self.limit_ = value
        return self

    def offset(self, value: int | None, *, is_page: bool = False) -> Self:
        """Adds an OFFSET clause to the query.

        Args:
            value (int | None): The number of records to skip.
            is_page (bool): If True, treats the value as a page number.

        Returns:
            Self: The current query object.

        """
        if is_page and value is not None and value > 0:
            if self.limit_ is None:
                raise ValueError("Need set limit")
            self.offset_ = (value - 1) * self.limit_
        else:
            self.offset_ = value
        return self

    def order_by(self, fields: list[str]) -> Self:
        """Adds an ORDER BY clause to the query.

        Args:
            fields (list[str]): The fields to order by.

        Returns:
            Self: The current query object.

        """
        self.order_by_ = fields
        return self

    def group_by(self, fields: list[str]) -> Self:
        """Adds a GROUP BY clause to the query.

        Args:
            fields (list[str]): The fields to group by.

        Returns:
            Self: The current query object.

        """
        self.group_by_ = fields
        return self

    @property
    def query(self) -> str:
        """Builds the SQL query string.

        Returns:
            str: The constructed SQL query.

        """

        match self._type:
            case QueryType.SELECT:
                return self._consturuct_select_query()
            case QueryType.INSERT:
                return self._construct_insert_query()
            case QueryType.UPDATE:
                return self._construct_update_query()
            case QueryType.DELETE:
                return self._construct_delete_query()
            case _:
                raise ValueError("Query type not set or unsupported.")

    def _consturuct_select_query(self) -> str:
        """Construct SELECT query."""
        query = f"SELECT {', '.join(self.columns_) if self.columns_ else '*'} FROM {self._table_name}"
        if self.conditions_:
            query += f" WHERE {' AND '.join(self.conditions_)}"
        if self.group_by_:
            query += f" GROUP BY {', '.join(self.group_by_)}"
        if self.order_by_:
            query += f" ORDER BY {', '.join(self.order_by_)}"
        if self.limit_ is not None:
            query += f" LIMIT {self.limit_}"
        if self.offset_ is not None:
            query += f" OFFSET {self.offset_}"
        return query

    def _construct_insert_query(self) -> str:
        """Construct INSERT query."""
        columns = ", ".join(self.columns_)
        values = ", ".join([f"({', '.join(map(decode_ch_value, value))})" for value in self.values_])
        query = f"INSERT INTO {self._table_name} ({columns}) VALUES {values}"
        return query

    def _construct_update_query(self) -> str:
        """Construct UPDATE query."""
        set_clause = ", ".join([f"{key} = {decode_ch_value(value)}" for key, value in self.set_values_.items()])
        query = f"UPDATE {self._table_name} SET {set_clause}"
        if self.conditions_:
            query += f" WHERE {' AND '.join(self.conditions_)}"
        return query

    def _construct_delete_query(self) -> str:
        """Construct DELETE query."""
        query = f"DELETE FROM {self._table_name}"
        if self.conditions_:
            query += f" WHERE {' AND '.join(self.conditions_)}"
        return query


def _get_field_extra(field: FieldInfo, field_name: str, body_class_name: str) -> dict[str, Any] | None:
    """Get extra schema information for a field."""
    if callable(field.json_schema_extra):
        logger.warning(
            "Filter schema extra for field %s.%s is not a dict, but a callable",
            body_class_name,
            field_name,
        )
        return None

    if field.json_schema_extra is not None:
        return field.json_schema_extra

    if hasattr(field, "_inititial_kwargs"):
        return field._inititial_kwargs

    return {}


def _process_field_value(field_value: Any, filter_type: FilterType) -> Any:
    """Process field value for specific filter types."""
    if filter_type in (FilterType.like, FilterType.ilike):
        field_value = field_value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_").replace("~", "\\~")
        field_value = field_value + "%"
    return field_value


def add_filters_to_query(body: BaseSchema) -> list[str]:
    """Add filter to query.

    Args:
        body (Any): Filter body.

    Returns:
        list[str]: Query conditions.

    """
    query_conditions: list[str] = []

    for field_name, field in body.model_fields.items():
        field_value = getattr(body, field_name)
        if field_value is None:
            continue

        extra = _get_field_extra(field, field_name, body.__class__.__name__)
        if extra is None:
            continue

        table_column = extra.get("table_column", field_name)
        filter_type = extra.get("filter_type", FilterType.eq)
        # Skip filters
        if filter_type == FilterType.skip:
            logger.debug(
                "Skipping filter by %s with %s and %s",
                table_column,
                filter_type,
                field_value,
            )
            continue

        logger.debug("Filtering by %s with %s and %s", table_column, filter_type, field_value)

        processed_value = _process_field_value(field_value, filter_type)
        ch_field_value = decode_ch_value(processed_value)
        _add_filter_to_query(query_conditions, table_column, ch_field_value, filter_type)

    return query_conditions


def _add_filter_to_query(
    query_conditions: list[str],
    table_column: str,
    ch_field_value: str,
    filter_type: FilterType,
) -> None:
    match filter_type:
        case FilterType.eq:
            query_conditions.append(f"{table_column} = {ch_field_value}")
        case FilterType.ne:
            query_conditions.append(f"{table_column} != {ch_field_value}")
        case FilterType.in_list:
            query_conditions.append(f"{table_column} IN {ch_field_value}")
        case FilterType.gt:
            query_conditions.append(f"{table_column} > {ch_field_value}")
        case FilterType.ge:
            query_conditions.append(f"{table_column} >= {ch_field_value}")
        case FilterType.lt:
            query_conditions.append(f"{table_column} < {ch_field_value}")
        case FilterType.le:
            query_conditions.append(f"{table_column} <= {ch_field_value}")
        case FilterType.like:
            query_conditions.append(f"{table_column} LIKE {ch_field_value}")
        case FilterType.ilike:
            query_conditions.append(f"{table_column} ILIKE {ch_field_value}")
        case _:
            raise NotImplementedError


async def get_pagination_data(clickhouse: ChClient, query: ChQuery, limit: int) -> tuple[int, int]:
    """Get the total number of rows and the number of pages based on filters.

    Args:
        clickhouse (ChClient): The ClickHouse client to execute the query.
        query (ChQuery): The query object containing the SQL query to execute.
        limit (int): The number of items per page.

    Returns:
        tuple[int, int]: A tuple containing the total number of items and the total number of pages.

    """
    result = await clickhouse.fetch(query.query)
    total_items = result[0]["total_items"]
    total_pages = (total_items + limit - 1) // limit
    return total_items, total_pages
