"""Sentry configuration."""

import logging
from os import environ
from typing import TYPE_CHECKING
from uuid import UUID

import sentry_sdk
from sentry_sdk.integrations import Integration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.litestar import LitestarIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


if TYPE_CHECKING:
    from sentry_sdk._types import Event, EventProcessor, Hint


def configure_sentry(
    dsn: str | None = None,
    *,
    asyncio_integration: bool = True,
    litestar_integration: bool = True,
) -> None:
    """Configure Sentry.

    Args:
        dsn (str, optional): Sentry DSN. If not provided, it will be read from
            the environment variable SENTRY_DSN. Defaults to None.
        asyncio_integration (bool, optional): Enable asyncio integration. Defaults to True.
        litestar_integration (bool, optional): Enable Litestar integration. Defaults to True.
    """
    dsn = dsn or environ.get("SENTRY_DSN")

    if dsn is None:
        return

    before_send: "EventProcessor | None" = None

    integrations = list[Integration]()
    integrations.append(LoggingIntegration(level=logging.DEBUG))

    if asyncio_integration:
        integrations.append(AsyncioIntegration())
    if litestar_integration:
        integrations.append(LitestarIntegration())
        before_send = _before_send_litestar

    sentry_sdk.init(
        dsn=dsn,
        enable_tracing=True,
        integrations=integrations,
        traces_sample_rate=0.5,
        before_send=before_send,
    )


def _before_send_litestar(event: "Event", _hint: "Hint") -> "Event":
    """Before send hook for Litestar.

    Sets event_id to request_id tag if it is available.

    Args:
        event (Event): Event to process.
        _hint (Hint): Hint.

    Returns:
        Event: Processed event.
    """
    request_id = event.get("tags", {}).get("request_id")

    if request_id is not None:
        try:
            request_uuid = UUID(request_id)
        except ValueError:
            return event
        event["event_id"] = request_uuid.hex

    return event
