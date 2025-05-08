"""Application exception handling.

This package provides custom exception types and handlers for the application,
allowing for consistent error handling and reporting.
"""

from app.lib.exceptions.base import (
    AbstractException,
    BadRequestException,
    ConflictException,
    ForbiddenException,
    InternalServerErrorException,
    NotFoundException,
    UnauthorizedException,
)
from app.lib.exceptions.filter import FilterException, FilterGroupAlreadyInUseException
from app.lib.exceptions.handler import ErrorSchema, abstract_exception_handler, register_exception_handlers


__all__ = [
    "AbstractException",
    "BadRequestException",
    "ConflictException",
    "ErrorSchema",
    "FilterException",
    "FilterGroupAlreadyInUseException",
    "ForbiddenException",
    "InternalServerErrorException",
    "NotFoundException",
    "UnauthorizedException",
    "abstract_exception_handler",
    "register_exception_handlers",
]
