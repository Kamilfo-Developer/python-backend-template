"""Idempotency config."""

from pydantic import Field

from app.lib.config.base import BaseSettings

FIVE_MINUTES = 60 * 5 * 1000


class IdempotencyConfig(BaseSettings):
    """Idempotency config."""

    ttl: int = Field(default=FIVE_MINUTES)
