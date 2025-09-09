"""Default exception handlers for FastAPI application."""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, create_model

from app.lib.exceptions.base import AbstractException
from app.lib.observability.fastapi import observe_exception

logger = logging.getLogger(__name__)


class ErrorSchema(BaseModel):
    """Error response schema for API exceptions."""

    detail: str | None = Field(
        description="Optional exception detail. Public and can be showed to the user.",
        examples=["Service 1 not found."],
    )
    error_code: str = Field(
        description="Exception name.",
        examples=["ServiceNotFoundException"],
    )
    additional_info: dict[str, Any] = Field(
        description="Additional computer-readable information.",
        examples=[{}],
    )


def to_error_schema(exc_list: list[type[AbstractException]]) -> type[ErrorSchema]:
    """Convert exceptions to an error schema."""
    return create_model(
        "ErrorSchemaFor" + "And".join([exc.__name__ for exc in exc_list]),
        error_code=(
            str,
            Field(
                description=" OR ".join([exc.__name__ for exc in exc_list]),
                examples=[" OR ".join([exc.__name__ for exc in exc_list])],
            ),
        ),
        detail=(
            str | None,
            Field(
                description=" OR ".join([exc.detail for exc in exc_list]),
                examples=[" OR ".join([exc.detail for exc in exc_list])],
            ),
        ),
        __base__=ErrorSchema,
    )


async def abstract_exception_handler(
    request: Request,
    exc: AbstractException,
) -> JSONResponse:
    """Exception handler for AbstractException.

    Returns:
        JSONResponse: JSON serialized ErrorModel.

    """
    if not exc.is_public:
        return await unknown_exception_handler(request, exc)

    error_schema = ErrorSchema(
        error_code=exc.__class__.__name__,
        detail=exc.current_detail,
        additional_info=exc.current_additional_info,
    ).model_dump(mode="json")

    return JSONResponse(
        status_code=exc.current_status_code,
        content=error_schema,
        headers=exc.current_headers,
    )


async def unknown_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Exception handler for unknown exceptions.

    Returns:
        JSONResponse: JSON serialized ErrorModel.

    """
    logger.exception("Unknown exception occurred. Details:", exc_info=exc)

    error_schema = ErrorSchema(
        error_code="UnknownException",
        detail="Unknown exception occurred.",
        additional_info={},
    ).model_dump(mode="json")

    return JSONResponse(status_code=500, content=error_schema)


async def unknown_exception_handler_with_observability(request: Request, exc: Exception) -> JSONResponse:
    """Exception handler for unknown exceptions with observability."""
    await observe_exception(exc)
    return await unknown_exception_handler(request, exc)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Exception handler for HTTPException.

    Returns:
        JSONResponse: JSON serialized ErrorModel.

    """

    error_schema = ErrorSchema(
        error_code="Exception",
        detail=exc.detail,
        additional_info={},
    ).model_dump(mode="json")

    return JSONResponse(status_code=exc.status_code, content=error_schema)


async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Exception handler for RequestValidationError.

    Returns:
        JSONResponse: JSON serialized ErrorModel.

    """
    errors = exc.errors()

    for error in errors:
        if "ctx" in error:
            del error["ctx"]
        if "url" in error:
            del error["url"]

    error_schema = ErrorSchema(
        error_code="ValidationException",
        detail="Invalid request data.",
        additional_info={"errors": errors},
    ).model_dump(mode="json")

    return JSONResponse(status_code=422, content=error_schema)


async def not_found_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Exception handler for 404.

    Returns:
        JSONResponse: JSON serialized ErrorModel.

    """
    error_schema = ErrorSchema(
        error_code="EndpointNotFoundException",
        detail="404 endpoint not found.",
        additional_info={},
    ).model_dump(mode="json")

    error_schema["additional_info"]["urls"] = {
        "openapi": "/openapi.json",
        "docs": "/docs",
    }

    return JSONResponse(status_code=404, content=error_schema)


def register_exception_handlers(app: FastAPI, *, should_observe_exceptions: bool = False) -> None:
    """Register exception handlers with the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application.
        should_observe_exceptions (bool): Whether to observe exceptions.

    """

    app.add_exception_handler(AbstractException, abstract_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(
        RequestValidationError,
        request_validation_exception_handler,  # type: ignore[arg-type]
    )

    if should_observe_exceptions:
        app.add_exception_handler(Exception, unknown_exception_handler_with_observability)
        return

    app.add_exception_handler(Exception, unknown_exception_handler)
