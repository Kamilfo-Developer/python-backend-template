"""Default exception handlers for FastAPI application."""

import logging
from typing import Any
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.lib.exceptions.base import AbstractException, NotFoundException

logger = logging.getLogger(__name__)

EMPTY_EXCEPTION_UUID = "00000000-0000-0000-0000-000000000000"


class ErrorSchema(BaseModel):
    """Error response schema for API exceptions."""

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


async def base_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for BaseAPIException and its subclasses."""
    error_schema = ErrorSchema(
        error_code=exc.__class__.__name__,
        detail=exc.detail,
        event_id=request.state.request_id or EMPTY_EXCEPTION_UUID,
        additional_info={},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_schema.model_dump_json(),
        headers=exc.headers,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for validation errors."""
    return JSONResponse(str(exc), status_code=422)


async def not_found_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for not found errors."""
    return await base_exception_handler(request, exc)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for FastAPI's HTTPException."""
    error_schema = ErrorSchema(
        error_code="HTTPException",
        detail=exc.detail,
        event_id=request.state.request_id or EMPTY_EXCEPTION_UUID,
        additional_info={},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_schema.model_dump_json(),
    )


async def unknown_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for unknown exceptions."""
    logger.exception("Unknown exception occurred")
    error_schema = ErrorSchema(
        error_code="UnknownException",
        detail="An unexpected error occurred",
        event_id=request.state.request_id or EMPTY_EXCEPTION_UUID,
        additional_info={},
    )
    return JSONResponse(
        status_code=500,
        content=error_schema.model_dump_json(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers with the FastAPI application."""

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(NotFoundException, not_found_exception_handler)
    app.add_exception_handler(AbstractException, base_exception_handler)
    app.add_exception_handler(Exception, unknown_exception_handler)
