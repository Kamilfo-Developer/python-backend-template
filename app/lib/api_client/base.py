"""Base API client."""

from logging import Logger
from typing import Any, Literal, Self, TypeVar, overload

from aiohttp import ClientError, ClientSession
from pydantic import BaseModel

from app.version import __version__

from .exception import ClientError as APIClientError

_ResponseSchema = TypeVar("_ResponseSchema", bound=BaseModel)


class BaseApiClient:
    """Base API client."""

    _api_prefix: str = ""
    """API prefix.

    Example: "api/v1/"
    """
    _ua: str = "resale-manager"
    """User agent.

    Example: "resale-manager"
    """
    _logger: Logger

    def __init__(
        self,
        connection_url: str,
        *,
        client_session: ClientSession | None = None,
        headers: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the API client.

        Args:
            connection_url (str): Connection URL.
            client_session (ClientSession, optional): Aiohttp client session. Defaults to None.
            headers (dict[str, Any], optional): Headers that will be added to all requests. Defaults to None.

        """
        self._connection_url = f"{connection_url.rstrip('/')}/{self._api_prefix}"
        self._client_session = client_session
        self._own_session = client_session is None
        self._ua_full = f"{self._ua}/{__version__}"
        self._headers = headers or {}

    async def __aenter__(self) -> Self:
        """Enter the async context manager."""
        if self._own_session:
            self._client_session = ClientSession()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the async context manager."""
        if self._own_session and self._client_session:
            await self._client_session.close()
            self._client_session = None

    @property
    def _session(self) -> ClientSession:
        """Get the client session."""
        if not self._client_session:
            raise RuntimeError("No client session initialized. Perhaps you forgot to use 'async with'.")
        return self._client_session

    @overload
    async def _request(
        self,
        method: Literal["GET", "POST", "PATCH", "DELETE", "PUT"],
        path: str,
        *,
        response_schema: type[_ResponseSchema],
        request_schema: BaseModel | None = None,
        **kwargs: Any,
    ) -> _ResponseSchema: ...

    @overload
    async def _request(
        self,
        method: Literal["GET", "POST", "PATCH", "DELETE", "PUT"],
        path: str,
        *,
        response_schema: None = None,
        request_schema: BaseModel | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]: ...

    async def _request(
        self,
        method: Literal["GET", "POST", "PATCH", "DELETE", "PUT"],
        path: str,
        *,
        response_schema: type[_ResponseSchema] | None = None,
        request_schema: BaseModel | None = None,
        **kwargs: Any,
    ) -> _ResponseSchema | dict[str, Any]:
        """Make a request.

        Args:
            method (Literal["GET", "POST", "PATCH", "DELETE", "PUT"]): Request method.
            path (str): Request path.
            response_schema (Type[BaseModel], optional): Response schema. Defaults to None.
            request_schema (BaseModel, optional): Request schema. Defaults to None.
            **kwargs (Any): Request kwargs. Passed to aiohttp.ClientSession.request.

        Returns:
            BaseModel | None: Response schema.

        """
        request_kwargs = self._get_request_kwargs(path, request_schema, **kwargs)
        # Make the request
        try:
            async with self._session.request(method, **request_kwargs) as resp:
                if not resp.ok:
                    self._logger.debug("Server answer: " + await resp.text(errors="replace"))
                resp.raise_for_status()
                answer = await resp.json()
        except (TimeoutError, ClientError) as error:
            self._logger.error(f"Server error:\n{error}")
            raise APIClientError(error)

        if response_schema is None:
            return answer
        # Convert response to response_schema
        return response_schema.model_validate(answer)

    def _get_request_kwargs(
        self,
        path: str,
        request_schema: BaseModel | None = None,
        disable_content_type: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get kwargs for request.

        Args:
            path (str): Request path.
            request_schema (BaseModel, optional): Request schema. Defaults to None.
            disable_content_type (bool, optional): Whether to disable the content type header. Defaults to False.
            **kwargs (Any): Additional request kwargs.

        Returns:
            dict[str, Any]: Request kwargs.
        <<<<<<< HEAD

        =======
        >>>>>>> feature-project-structure

        """
        # Set default headers
        headers = self._headers | kwargs.pop("headers", {})
        headers["User-Agent"] = self._ua_full
        if not disable_content_type:
            headers["Content-Type"] = headers.get("Content-Type", "application/json")
        # Convert request_schema to json if it exists
        if request_schema is not None:
            kwargs["json"] = request_schema.model_dump(mode="json")

        return {"url": f"{self._connection_url}{path}", "headers": headers} | kwargs
