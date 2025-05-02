"""Request id middleware."""

from uuid import uuid4

from litestar.enums import ScopeType
from litestar.middleware import ASGIMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send
from sentry_sdk import configure_scope


class RequestIdMiddleware(ASGIMiddleware):
    """Middleware to generate a request_id and set it in the request state.

    Used for tracking errors.
    """

    async def handle(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
        next_app: ASGIApp,
    ) -> None:
        """Process the ASGI request.

        Args:
            scope (Scope): The ASGI connection scope.
            receive (Receive): The ASGI receive function.
            send (Send): The ASGI send function.
            next_app (ASGIApp): The ASGI application.

        """
        if scope["type"] != ScopeType.HTTP:
            # Pass through non-HTTP requests unchanged
            await next_app(scope, receive, send)
            return
        # Generate a new UUID4
        request_id = uuid4()
        # Set the request_id in the scope state
        scope["state"]["request_id"] = request_id
        # Set the request_id in Sentry scope
        with configure_scope() as sentry_scope:
            sentry_scope.set_tag("request_id", request_id.hex)

        await next_app(scope, receive, send)
