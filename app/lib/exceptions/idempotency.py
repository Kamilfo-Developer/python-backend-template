"""Idempotency exceptions."""

from app.lib.exceptions.base import AbstractException, ConflictException


class IdempotencyException(AbstractException):
    """Idempotency exception."""


class IdempotentRequest(IdempotencyException, ConflictException):
    """Idempotent request."""

    detail = "Idempotent request"
