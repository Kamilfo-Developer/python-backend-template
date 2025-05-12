"""Idempotent request middleware."""

from collections.abc import Awaitable, Callable
from hashlib import sha256
from typing import Any

from cbor2 import dumps as cbor2_dumps, loads as cbor2_loads
from fastapi import Request, Response
from redis.asyncio import Redis
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class IdempotentRequestMiddleware(BaseHTTPMiddleware):
    """Middleware to handle idempotent requests using Redis for caching responses.

    This middleware checks for an 'X-Idempotency-Key' in the request headers and uses it to cache
    responses for POST, PUT, and PATCH requests. If a request with the same idempotency key is
    received, the cached response is returned instead of processing the request again.
    """

    allowed_methods = {"POST", "PUT", "PATCH"}
    _redis_key = "request:{key}"

    def __init__(
        self,
        app: ASGIApp,
        dependencies_getter: Callable[[type[Any]], Any],
        ttl: int = 120,
    ) -> None:
        """Initialize the idempotent request middleware.

        Args:
            app (ASGIApp): The ASGI application instance.
            dependencies_getter (Callable[[str], Any]): The function to get dependencies.
            ttl (int): Time-to-live for cached responses in seconds. Default is 120 seconds.

        """
        super().__init__(app)

        self._dependencies_getter = dependencies_getter
        self._ttl = ttl

    async def dispatch(self, request: Request, call_next: Callable[..., Awaitable[Any]]) -> Any:
        """Process the incoming request and return a response.

        Checks for an 'Idempotency-Key' in the request headers and uses it to determine if the
        request should be processed or if a cached response should be returned.

        Args:
            request (Request): The incoming HTTP request.
            call_next (Callable[..., Awaitable[Any]]): The next middleware or endpoint to call.

        Returns:
            Any: The HTTP response, either from cache or freshly processed.

        """
        idempotency_key = request.headers.get("X-Idempotency-Key")

        if not (idempotency_key and request.method in self.allowed_methods):
            return await call_next(request)

        return await self._handle_request(
            idempotency_key,
            await self._dependencies_getter(Redis),
            request,
            call_next,
        )

    async def _handle_request(
        self,
        idempotency_key: str,
        redis: Redis,
        request: Request,
        call_next: Callable[..., Awaitable[Any]],
    ) -> Response:
        """Handle the request by checking and storing the response in Redis.

        Args:
            idempotency_key (str): The key used to identify idempotent requests.
            redis (Redis): The Redis client instance.
            request (Request): The incoming HTTP request.
            call_next (Callable[..., Awaitable[Any]]): The next middleware or endpoint to call.

        Returns:
            Response: The HTTP response, either from cache or freshly processed.

        """
        request_body = await request.body()
        key = sha256(
            request.method.encode() + request.url.path.encode() + request_body + idempotency_key.encode(),
        ).hexdigest()
        redis_key = self._redis_key.format(key=key)
        # Check if cached response exists
        if cached_response := await redis.get(redis_key):
            cached_data = cbor2_loads(cached_response)
            return Response(
                content=cached_data["body"],
                media_type=cached_data["headers"].get("content-type", "application/json"),
                headers={k: v for k, v in cached_data["headers"].items() if k.lower() != "content-type"},
                status_code=cached_data["status_code"],
            )
        # Process the request
        response = await call_next(request)
        # Cache the response if it is successful
        if response.status_code < 400:
            response_body = [chunk async for chunk in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(response_body))

            response_body_bytes = b"".join(response_body)
            # Prepare data for caching
            cached_data = {
                "body": response_body_bytes,
                "headers": dict(response.headers),
                "status_code": response.status_code,
            }
            # Encode and store in Redis
            await redis.set(redis_key, cbor2_dumps(cached_data), ex=self._ttl)

        return response
