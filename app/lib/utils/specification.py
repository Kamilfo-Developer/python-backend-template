"""Specification pattern implementation."""

import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from app.lib.enums.filter import OrderByType
from app.lib.utils.rattrs import rgetattr


class BaseSpecification(ABC):
    """The base specification class to implement the Specification pattern."""

    field: str
    value: Any

    def __init__(self, field: str, value: Any) -> None:
        """Initialize the specification object.

        Args:
            field (str): A field to use in is_satisfied_by.
            value (Any): A value of the field to use in is_satisfied_by.

        """
        self.field = field
        self.value = value

    @abstractmethod
    def is_satisfied_by(self, obj: Any) -> bool:
        """Whether the obj specifies the specification condition.

        Args:
            obj (Any): Any object.

        Returns:
            bool: The result of applying the predicate to the object.

        """


class EqualsSpecification(BaseSpecification):
    """Specification that checks if the field of an object is equal to a value."""

    def __init__(self, field: str, value: Any) -> None:
        super().__init__(field, value)

    def is_satisfied_by(self, obj: Any) -> bool:
        """Whether the obj specifies the equals specification condition.

        Args:
            obj (Any): Any object.

        Returns:
            bool: The result of applying the predicate to the object.

        """
        return rgetattr(obj, self.field) == self.value


class NotEqualsSpecification(BaseSpecification):
    """Specification that checks if the field of an object is not equal to a value."""

    def __init__(self, field: str, value: Any) -> None:
        super().__init__(field, value)

    def is_satisfied_by(self, obj: Any) -> bool:
        """Whether the obj specifies the not equals specification condition.

        Args:
            obj (Any): Any object.

        Returns:
            bool: The result of applying the predicate to the object.

        """
        return rgetattr(obj, self.field) != self.value


class GreaterThanSpecification(BaseSpecification):
    """Specification that checks if the field of an object is greater than a value."""

    def __init__(self, field: str, value: Any) -> None:
        super().__init__(field, value)

    def is_satisfied_by(self, obj: Any) -> bool:
        """Whether the obj specifies the greater than specification condition.

        Args:
            obj (Any): Any object.

        Returns:
            bool: The result of applying the predicate to the object.

        """
        return rgetattr(obj, self.field) > self.value


class LessThanSpecification(BaseSpecification):
    """Specification that checks if the field of an object is less than a value."""

    def __init__(self, field: str, value: Any) -> None:
        super().__init__(field, value)

    def is_satisfied_by(self, obj: Any) -> bool:
        """Whether the obj specifies the less than specification condition.

        Args:
            obj (Any): Any object.

        Returns:
            bool: The result of applying the predicate to the object.

        """
        return rgetattr(obj, self.field) < self.value


class GreaterThanOrEqualsToSpecification(BaseSpecification):
    """Specification that checks if the field of an object is greater than or equals to a value."""

    def __init__(self, field: str, value: Any) -> None:
        super().__init__(field, value)

    def is_satisfied_by(self, obj: Any) -> bool:
        """Whether the obj specifies the greater than or equals to specification condition.

        Args:
            obj (Any): Any object.

        Returns:
            bool: The result of applying the predicate to the object.

        """
        return rgetattr(obj, self.field) >= self.value


class LessThanOrEqualsToSpecification(BaseSpecification):
    """Specification that checks if the field of an object is greater than or equals to a value."""

    def __init__(self, field: str, value: Any) -> None:
        super().__init__(field, value)

    def is_satisfied_by(self, obj: Any) -> bool:
        """Whether the obj specifies the greater than or equals to specification condition.

        Args:
            obj (Any): Any object.

        Returns:
            bool: The result of applying the predicate to the object.

        """
        return rgetattr(obj, self.field) <= self.value


class FunctionSpecification(BaseSpecification):
    """Specification that checks if the value of object satisfies some function."""

    func: Callable[[Any, str, Any], bool]

    def __init__(
        self,
        field: str,
        value: Any,
        func: Callable[[Any, str, Any], bool] = lambda _x, _y, _z: False,
    ) -> None:
        """Initialize the specification object.

        Args:
            field (str): A field to use in is_satisfied_by.
            value (Any): A value of the field to use in is_satisfied_by.
            func (Callable[[Any, str, Any], bool], optional):
                A function to use in is_satisfied_by, takes obj: Any, field: str, value: Any.
                Defaults to function which always returns False.

        """
        self.field = field
        self.value = value
        self.func = func

    def is_satisfied_by(self, obj: Any) -> bool:
        """Whether the obj specifies the function specification condition.

        Args:
            obj (Any): Any object.

        Returns:
            bool: The result of applying the predicate to the object.

        """
        return self.func(obj, self.field, self.value)


class InListSpecification(BaseSpecification):
    """Specification that checks if the field of an object is in a value, where value is a list."""

    def __init__(self, field: str, value: list[Any]) -> None:
        super().__init__(field, value)

    def is_satisfied_by(self, obj: Any) -> bool:
        """Whether the obj specifies the in list specification condition.

        Args:
            obj (Any): Any object.

        Returns:
            bool: The result of applying the predicate to the object.

        """

        return rgetattr(obj, self.field) in self.value


class NotInListSpecification(BaseSpecification):
    """Specification that checks if the field of an object is not in a value, where value is a list."""

    def __init__(self, field: str, value: list[Any]) -> None:
        super().__init__(field, value)

    def is_satisfied_by(self, obj: Any) -> bool:
        """Whether the obj specifies the not in list specification condition.

        Args:
            obj (Any): Any object.

        Returns:
            bool: The result of applying the predicate to the object.

        """
        return rgetattr(obj, self.field) not in self.value


class SubListSpecification(BaseSpecification):
    """Specification that checks if the field of an object is a sublist of a value, where value is a list."""

    def __init__(self, field: str, value: list[Any]) -> None:
        super().__init__(field, value)

    def is_satisfied_by(self, obj: Any) -> bool:
        """Whether the obj specifies the sublist specification condition.

        Args:
            obj (Any): Any object.

        Returns:
            bool: The result of applying the predicate to the object.

        """

        return set(self.value).issubset(set(rgetattr(obj, self.field)))


class NotSubListSpecification(BaseSpecification):
    """Specification that checks if the field of an object is not a sublist of a value, where value is a list."""

    def __init__(self, field: str, value: list[Any]) -> None:
        super().__init__(field, value)

    def is_satisfied_by(self, obj: Any) -> bool:
        """Whether the obj specifies the not sublist specification condition.

        Args:
            obj (Any): Any object.

        Returns:
            bool: The result of applying the predicate to the object.

        """

        return not set(self.value).issubset(set(rgetattr(obj, self.field)))


class LikeSpecification(BaseSpecification):
    """Specification that checks if the field is like a value. Works as the SQL LIKE operator."""

    def __init__(self, field: str, value: str) -> None:
        super().__init__(field, value)

    def is_satisfied_by(self, obj: Any) -> bool:
        """Whether the obj specifies the like specification condition.

        Args:
            obj (Any): Any object.

        Returns:
            bool: The result of applying the predicate to the object.

        """
        return re.match(self.value.replace("%", ".*").replace(".", r"\."), rgetattr(obj, self.field)) is not None


class ILikeSpecification(BaseSpecification):
    """Specification that checks if the field is ilike a value. Works as the SQL ILIKE operator."""

    def __init__(self, field: str, value: str) -> None:
        super().__init__(field, value)

    def is_satisfied_by(self, obj: Any) -> bool:
        """Whether the obj specifies the ilike specification condition.

        Args:
            obj (Any): Any object.

        Returns:
            bool: The result of applying the predicate to the object.

        """
        return (
            re.match(self.value.replace("%", ".*").replace(".", r"\."), rgetattr(obj, self.field).lower()) is not None
        )


class OrderBySpecification:
    """Order by specification."""

    field: str
    type: OrderByType

    def __init__(self, field: str, type: OrderByType) -> None:
        self.field = field
        self.type = type
