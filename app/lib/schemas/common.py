"""Common schemas for the API."""

from dataclasses import dataclass


@dataclass
class OKSchema:
    """OK Schema."""

    ok: bool = True
