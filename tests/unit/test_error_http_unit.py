from __future__ import annotations

import httpx
import pytest
from api_client_kit.client.models import ResponseData
from api_client_kit.errors import (
    ApiClientError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    HttpStatusError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)

pytestmark = [pytest.mark.unit]


def test_http_status_error_has_the_expected_hierarchy() -> None:
    assert issubclass(HttpStatusError, ApiClientError)
    assert issubclass(HttpStatusError, Exception)


@pytest.mark.parametrize(
    "error_type",
    [
        AuthenticationError,
        AuthorizationError,
        NotFoundError,
        ConflictError,
        ValidationError,
        RateLimitError,
        ServerError,
    ],
)
def test_specialized_http_errors_have_the_expected_hierarchy(
    error_type: type[HttpStatusError],
) -> None:
    assert issubclass(error_type, HttpStatusError)
    assert issubclass(error_type, ApiClientError)
    assert issubclass(error_type, Exception)


def test_http_status_error_preserves_response_and_base_behavior() -> None:
    raw_response = httpx.Response(418)
    response = ResponseData(raw=raw_response)

    error = HttpStatusError("HTTP request failed", response=response)

    assert error.args == ("HTTP request failed",)
    assert error.response is response
    assert error.response.raw is raw_response
    assert error.context is None
    assert str(error) == "HTTP request failed"
    assert repr(error) == "HttpStatusError('HTTP request failed')"
    assert not hasattr(error, "raw")
    assert not hasattr(error, "raw_response")
    assert not hasattr(error, "httpx_response")
    assert not hasattr(error, "status_code")


def test_http_status_error_requires_keyword_only_response() -> None:
    with pytest.raises(TypeError):
        HttpStatusError("HTTP request failed")  # type: ignore[call-arg]


def test_http_status_error_inherits_context_support() -> None:
    response = ResponseData(raw=httpx.Response(418))

    error = HttpStatusError(
        "HTTP request failed",
        response=response,
        context={"status_code": 418, "method": "GET"},
    )

    assert error.context == {"status_code": 418, "method": "GET"}


@pytest.mark.parametrize(
    ("error_type", "status_code"),
    [
        (AuthenticationError, 401),
        (AuthorizationError, 403),
        (NotFoundError, 404),
        (ConflictError, 409),
        (ValidationError, 422),
        (RateLimitError, 429),
        (ServerError, 500),
    ],
)
def test_specialized_http_errors_preserve_base_behavior(
    error_type: type[HttpStatusError],
    status_code: int,
) -> None:
    response = ResponseData(raw=httpx.Response(status_code))

    error = error_type("HTTP request failed", response=response)

    assert type(error) is error_type
    assert isinstance(error, HttpStatusError)
    assert isinstance(error, ApiClientError)
    assert error.response is response
    assert str(error) == "HTTP request failed"
    assert repr(error) == f"{error_type.__name__}('HTTP request failed')"


def test_http_status_error_does_not_render_response_or_context_secrets() -> None:
    raw_response = httpx.Response(
        500,
        headers={"X-Test-Secret": "test-http-response-secret"},
        content=b"test-http-response-secret",
    )
    response = ResponseData(raw=raw_response)
    error = HttpStatusError(
        "HTTP request failed",
        response=response,
        context={"authorization": "Bearer test-http-context-secret"},
    )

    assert "test-http-response-secret" not in str(error)
    assert "test-http-response-secret" not in repr(error)
    assert "test-http-context-secret" not in str(error)
    assert "test-http-context-secret" not in repr(error)


def test_http_status_error_supports_native_exception_chaining() -> None:
    response = ResponseData(raw=httpx.Response(500))
    original = ValueError("upstream detail")

    with pytest.raises(HttpStatusError) as exc_info:
        raise HttpStatusError("HTTP request failed", response=response) from original

    error = exc_info.value
    assert error.__cause__ is original
    assert isinstance(error.__cause__, ValueError)
    assert error.args == ("HTTP request failed",)
    assert error.response is response
