"""Default exception handlers for the intape package."""

import logging
from typing import Any
from uuid import UUID

from litestar import Litestar, Request, Response
from litestar.datastructures import State
from litestar.exceptions import HTTPException, NotFoundException, ValidationException
from pydantic import BaseModel, Field

from app.lib.exceptions.base import AbstractException

logger = logging.getLogger(__name__)

EMPTY_EXCEPTION_UUID = "00000000-0000-0000-0000-000000000000"


class ErrorSchema(BaseModel):
    """Error response for AbstractException."""

    detail: str | None = Field(
        description="Optional exception detail. Public and can be showed to the user.",
        examples=["Service 1 not found."],
    )
    error_code: str = Field(description="Exception name.", examples=["ServiceNotFoundException"])
    event_id: str | UUID = Field(
        description="Exception event UUID. Can be used to track exceptions. "
        "Can be provided to support team to request for more details. "
        "If it equals zero, then exception is not tracked.",
    )
    additional_info: dict[str, Any] = Field(
        description="Additional computer-readable information.",
        examples=[{"service_id": 1}],
    )


def abstract_exception_handler(
    request: Request[None, None, State],
    exc: AbstractException,
    log: bool = True,
) -> Response[ErrorSchema]:
    """Exception handler for AbstractException.

    Returns:
        JSONResponse: JSON serialized ErrorModel.

    """
    if log:
        exc._log()

    if exc.current_request_id is None:
        exc.current_request_id = request.state["request_id"]

    if not exc.is_public:
        return unknown_exception_handler(request, exc)

    error_schema = ErrorSchema(
        error_code=exc.__class__.__name__,
        detail=exc.current_detail,
        event_id=str(exc.current_request_id),
        additional_info=exc.current_additional_info,
    )

    return Response(
        status_code=exc.current_status_code,
        content=error_schema,
        headers=exc.current_headers,
    )


def unknown_exception_handler(request: Request[None, None, State], exc: Exception) -> Response[ErrorSchema]:
    """Exception handler for unknown exceptions.

    Returns:
        JSONResponse: JSON serialized ErrorModel.

    """
    id_: str | None = request.state.get("request_id")
    if not id_:
        raise RuntimeError("There is no request_id in the state of the application")
    logger.exception(f"({id_}) Unknown exception occurred. Details:")

    error_schema = ErrorSchema(
        error_code="UnknownException",
        detail="Unknown exception occurred.",
        event_id=str(id_),
        additional_info={},
    )

    return Response(status_code=500, content=error_schema)


def http_exception_handler(request: Request[None, None, State], exc: HTTPException) -> Response[ErrorSchema]:
    """Exception handler for HTTPException.

    Returns:
        Respoonse: JSON serialized ErrorModel.

    """
    id_: UUID = request.state["request_id"]
    logger.exception(f"({id_}) Raw HTTPException occurred. Details:")

    error_schema = ErrorSchema(
        error_code="Exception",
        detail=exc.detail,
        event_id=str(id_),
        additional_info={},
    )

    return Response(status_code=exc.status_code, content=error_schema)


def request_validation_exception_handler(
    request: Request[None, None, State],
    exc: ValidationException,
) -> Response[ErrorSchema]:
    """Exception handler for RequestValidationError.

        ValidationException: request_validation_exception_handler,

    Returns:
        JSONResponse: JSON serialized ErrorModel.

    """
    error_schema = ErrorSchema(
        error_code="ValidationException",
        detail="Invalid request data.",
        event_id=EMPTY_EXCEPTION_UUID,
        additional_info={"error": exc},
    )

    return Response(status_code=422, content=error_schema)


def not_found_exception_handler(request: Request[None, None, State], exc: HTTPException) -> Response[ErrorSchema]:
    """Exception handler for 404.

    Returns:
        JSONResponse: JSON serialized ErrorModel.

    """
    error_schema = ErrorSchema(
        error_code="EndpointNotFoundException",
        detail="404 endpoint not found.",
        event_id=EMPTY_EXCEPTION_UUID,
        additional_info={},
    )

    error_schema.additional_info["urls"] = {
        "openapi": "/openapi.json",
        "docs": "/docs",
    }

    return Response(status_code=404, content=error_schema)


def register_exception_handlers(app: Litestar) -> None:
    """Register default exception handlers.

    Args:
        app (Litestar): Litestar application.

    """
    app.exception_handlers = {
        ValidationException: request_validation_exception_handler,
        HTTPException: http_exception_handler,
        AbstractException: abstract_exception_handler,
        Exception: unknown_exception_handler,
        NotFoundException: not_found_exception_handler,
    }
