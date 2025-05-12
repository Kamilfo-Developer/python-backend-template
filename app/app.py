"""Module containing main FastAPI application."""

from fastapi import FastAPI

from app.dependencies.providers import app_provider
from app.lib.fastapi_app import FastAPIApp


def app() -> FastAPI:
    """Return FastAPI application instance for Uvicorn server."""
    return FastAPIApp.from_env([app_provider]).fastapi_app
