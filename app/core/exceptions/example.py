"""Example exceptions."""

from app.lib.exceptions.base import AbstractException, ConflictException, NotFoundException


class BaseExampleException(AbstractException):
    """Base example exception."""


class ExampleBusinessLogicException(BaseExampleException, ConflictException):
    """Business logic exception."""

    detail = "Something happened in business logic"


class NoSuchExample(BaseExampleException, NotFoundException):
    """Example not found."""

    detail = "Example not found"
