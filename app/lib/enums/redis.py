"""Redis key types."""

from .base import BaseEnum


class BaseRedisKeyType(BaseEnum):
    """Redis key type."""

    @property
    def _prefix(self) -> str:
        raise NotImplementedError


class AuthRedisKeyType(BaseRedisKeyType):
    """Auth redis key type."""

    _prefix = "auth"

    access = f"{_prefix}:access:{{token_id}}"
    """Key for access token."""


class ServiceRedisKeyType(BaseRedisKeyType):
    """Service redis key type."""

    _prefix = "service"

    downtime = f"{_prefix}:downtime:{{agent_id}}:{{service_id}}"
