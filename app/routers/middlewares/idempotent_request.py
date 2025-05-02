"""Idempotent request middleware."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from hashlib import sha256
from typing import Any

from cbor2 import dumps as cbor2_dumps
from cbor2 import loads as cbor2_loads
from litestar.datastructures import MutableScopeHeaders
from litestar.enums import ScopeType
from litestar.middleware import ASGIMiddleware
from litestar.types import ASGIApp, HTTPRequestEvent, Message, Receive, Scope, Send
from redis.asyncio import ConnectionPool, Redis

from app.core.dependencies import constructors as app_depends

FIRST_CLIENT_ERROR_HTTP_CODE = 400


class IdempotentRequestMiddleware(ASGIMiddleware):
    """Middleware to handle idempotent requests using Redis for caching responses.

    This middleware checks for an 'Idempotency-Key' in the request headers and uses it to cache
    responses for POST, PUT, and PATCH requests. If a request with the same idempotency key is
    received, the cached response is returned instead of processing the request again.
    """

    allowed_methods: set[str] = {"POST", "PUT", "PATCH"}
    _redis_key: str = "request:{key}"

    def __init__(
        self,
        ttl: int = 120,
    ) -> None:
        self._ttl = ttl

        self._redis_pool: ConnectionPool | None = None

    async def handle(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
        next_app: ASGIApp,
    ) -> None:
        """Process the ASGI request and return a response.

        Checks for an 'X-Idempotency-Key' in the request headers and uses it to determine if the
        request should be processed or if a cached response should be returned.

        Args:
            scope (Scope): The ASGI connection scope.
            receive (Receive): The ASGI receive function.
            send (Send): The ASGI send function.
            next_app (ASGIApp): The ASGI application.

        """
        if scope["type"] != ScopeType.HTTP:
            await next_app(scope, receive, send)
            return
        # Extract headers from scope
        headers = MutableScopeHeaders(scope)
        idempotency_key = headers.get("X-Idempotency-Key")
        method = scope["method"]

        if not (idempotency_key and method in self.allowed_methods):
            await next_app(scope, receive, send)
            return

        async with self._redis() as redis:
            # Need to capture request body
            body = await self._get_request_body(receive)
            # Create a key for the request
            key = sha256(
                method.encode() + scope["path"].encode() + body + idempotency_key.encode(),
            ).hexdigest()
            redis_key = self._redis_key.format(key=key)
            # Check if cached response exists
            if cached_response := await redis.get(redis_key):
                cached_data = cbor2_loads(cached_response)
                await self._send_cached_response(cached_data, send)
                return

            # Create new receive that returns the stored body
            async def new_receive() -> HTTPRequestEvent:
                return {"type": "http.request", "body": body, "more_body": False}

            # Create intercepting send
            response_chunks: list[bytes] = []
            response_headers: dict[str, str] = {}

            async def intercept_send(message: Message) -> None:
                response_status = 200
                if message["type"] == "http.response.start":
                    # Store headers
                    for name, value in message.get("headers", []):
                        response_headers[name.decode("latin-1")] = value.decode(
                            "latin-1",
                        )
                    # Pass through the message
                    await send(message)

                elif message["type"] == "http.response.body":
                    # Collect response chunks
                    chunk = message.get("body", b"")
                    if chunk:
                        response_chunks.append(chunk)
                    # Pass through the message
                    await send(message)
                    # If this is the last chunk and status is successful, cache the response
                    if not message.get("more_body", False) and response_status < FIRST_CLIENT_ERROR_HTTP_CODE:
                        response_body = b"".join(response_chunks)
                        cached_data = {
                            "body": response_body,
                            "headers": response_headers,
                            "status_code": response_status,
                        }
                        await redis.set(
                            redis_key,
                            cbor2_dumps(cached_data),
                            ex=self._ttl,
                        )
                else:
                    # Pass through other message types
                    await send(message)

            # Process the request with our intercepting send
            await next_app(scope, new_receive, intercept_send)

    async def _get_request_body(self, receive: Receive) -> bytes:
        """Receive and return the full request body.

        Args:
            receive (Receive): The ASGI receive function.

        Returns:
            bytes: The complete request body.

        """
        body = b""
        more_body = True

        while more_body:
            message = await receive()
            if message["type"] == "http.request":
                body += message.get("body", b"")
                more_body = message.get("more_body", False)

        return body

    async def _send_cached_response(
        self,
        cached_data: dict[str, Any],
        send: Send,
    ) -> None:
        """Send a cached response through the ASGI send function.

        Args:
            cached_data (Dict[str, Any]): The cached response data.
            send (Send): The ASGI send function.

        """
        # Prepare headers
        headers = []
        for name, value in cached_data["headers"].items():
            headers.append(
                (name.lower().encode("latin-1"), str(value).encode("latin-1")),
            )
        # Send response start
        await send(
            {
                "type": "http.response.start",
                "status": cached_data["status_code"],
                "headers": headers,
            },
        )
        # Send response body
        await send(
            {
                "type": "http.response.body",
                "body": cached_data["body"],
                "more_body": False,
            },
        )

    @asynccontextmanager
    async def _redis(self) -> AsyncGenerator[Redis, None]:
        """Create a Redis connection.

        Yields:
            Redis: An asynchronous generator yielding a Redis connection.

        """
        if not self._redis_pool:
            raise ValueError("Redis conn pool is not set")

        async with asynccontextmanager(app_depends.redis_conn)(
            self._redis_pool,
        ) as redis:
            yield redis
