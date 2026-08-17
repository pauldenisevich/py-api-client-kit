"""Structured package error exports."""

from __future__ import annotations

from api_client_kit.errors.base import ApiClientError
from api_client_kit.errors.network import NetworkError, TimeoutError  # noqa: A004

__all__ = (
    "ApiClientError",
    "NetworkError",
    "TimeoutError",
)
