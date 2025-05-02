"""Common exceptions for the API."""

from app.lib.exceptions.base import InternalServerErrorException


class DatabaseException(InternalServerErrorException):
    """Exception raises when a database error occurs."""


class CacheException(InternalServerErrorException):
    """Exception raises when a cache error occurs."""
