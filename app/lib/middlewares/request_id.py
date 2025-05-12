"""Request id middleware."""

from collections.abc import Awaitable, Callable
from typing import Any
from uuid import uuid4

from fastapi import Request
from sentry_sdk import configure_scope
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to generate a request_id and set it in the request state.

    Used for tracking errors.
    """

    async def dispatch(self, request: Request, call_next: Callable[..., Awaitable[Any]]) -> Any:
        """Generate a new UUID4 and set it in the request state.

        Args:
            request (Request): The incoming HTTP request.
            call_next (Callable[..., Awaitable[Any]]): The next middleware or endpoint to call.

        Returns:
            Any: The HTTP response, either from cache or freshly processed.

        """
        # Generate a new UUID4
        request_id = uuid4()
        # Set the request_id in the state so that it can be accessed later
        request.state.request_id = request_id
        # Set the request_id in Sentry scope
        with configure_scope() as scope:
            scope.set_tag("request_id", request_id.hex)
        # Call the next middleware
        return await call_next(request)
