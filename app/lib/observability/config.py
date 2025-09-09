"""Observability configuration."""

import os

from pydantic import Field
from pydantic_settings import BaseSettings


def get_enable_otel_tracer() -> bool:
    """Get if otel tracer is enabled."""
    return "OTEL_EXPORTER_OTLP_ENDPOINT" in os.environ


class ObservabilityConfig(BaseSettings):
    """Observability configuration."""

    service_namespace: str = "ChatBridge Dev"

    enable_otel_tracer: bool = Field(default_factory=get_enable_otel_tracer)
    enable_console_tracer: bool = False

    enable_otel_metrics: bool = Field(default_factory=get_enable_otel_tracer)
    enable_console_metrics: bool = False

    enable_otel_logs: bool = Field(default_factory=get_enable_otel_tracer)
    enable_console_logs: bool = False

    suppress_httpx_logs: bool = True
