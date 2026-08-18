from __future__ import annotations

import api_client_kit
import api_client_kit.errors as errors
import pytest
from api_client_kit.errors import (
    ApiClientError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    HttpStatusError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,  # noqa: A004
    ValidationError,
)

pytestmark = [pytest.mark.unit]


def test_errors_subpackage_exports_package_error_types() -> None:
    assert errors.__all__ == (
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
    )
    assert errors.ApiClientError is ApiClientError
    assert errors.NetworkError is NetworkError
    assert errors.TimeoutError is TimeoutError
    assert errors.HttpStatusError is HttpStatusError
    assert errors.AuthenticationError is AuthenticationError
    assert errors.AuthorizationError is AuthorizationError
    assert errors.NotFoundError is NotFoundError
    assert errors.ConflictError is ConflictError
    assert errors.ValidationError is ValidationError
    assert errors.RateLimitError is RateLimitError
    assert errors.ServerError is ServerError


def test_top_level_package_does_not_export_error_types() -> None:
    assert not hasattr(api_client_kit, "ApiClientError")
    assert not hasattr(api_client_kit, "NetworkError")
    assert not hasattr(api_client_kit, "TimeoutError")
    assert not hasattr(api_client_kit, "HttpStatusError")
    assert not hasattr(api_client_kit, "AuthenticationError")
    assert not hasattr(api_client_kit, "AuthorizationError")
    assert not hasattr(api_client_kit, "NotFoundError")
    assert not hasattr(api_client_kit, "ConflictError")
    assert not hasattr(api_client_kit, "ValidationError")
    assert not hasattr(api_client_kit, "RateLimitError")
    assert not hasattr(api_client_kit, "ServerError")


def test_safe_context_builder_remains_internal() -> None:
    assert "_build_error_context" not in errors.__all__
    assert not hasattr(errors, "_build_error_context")
    assert not hasattr(errors, "build_error_context")
    assert not hasattr(api_client_kit, "_build_error_context")
    assert not hasattr(api_client_kit, "build_error_context")
