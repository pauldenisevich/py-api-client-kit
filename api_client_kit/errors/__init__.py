"""Structured package error exports."""

from __future__ import annotations

from api_client_kit.errors.base import ApiClientError
from api_client_kit.errors.decode import DecodeError
from api_client_kit.errors.http import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    HttpStatusError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from api_client_kit.errors.network import NetworkError, TimeoutError  # noqa: A004

__all__ = (  # noqa: RUF022
    "ApiClientError",
    "NetworkError",
    "TimeoutError",
    "HttpStatusError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "DecodeError",
)
