"""Opinionated toolkit for building robust Python API clients."""

from __future__ import annotations

from api_client_kit.client import AsyncClient, RequestOptions, ResponseData, SyncClient

__version__ = "0.0.1"

__all__ = (
    "AsyncClient",
    "RequestOptions",
    "ResponseData",
    "SyncClient",
    "__version__",
)
