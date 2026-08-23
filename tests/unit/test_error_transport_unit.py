from __future__ import annotations

import httpx
import pytest
from api_client_kit.client.models import RequestContext
from api_client_kit.errors import NetworkError, TimeoutError  # noqa: A004
from api_client_kit.errors.transport import _transport_error_from_httpx

pytestmark = [pytest.mark.unit]


def test_transport_mapper_classifies_timeout_with_fixed_message() -> None:
    error = _transport_error_from_httpx(
        httpx.ReadTimeout("low-level timeout detail"),
        RequestContext("GET", "https://api.example.test"),
    )

    assert type(error) is TimeoutError
    assert str(error) == "HTTP request timed out"
    assert repr(error) == "TimeoutError('HTTP request timed out')"
    assert error.args == ("HTTP request timed out",)


def test_transport_mapper_classifies_non_timeout_transport_error_with_fixed_message() -> None:
    error = _transport_error_from_httpx(
        httpx.ConnectError("low-level connection detail"),
        RequestContext("GET", "https://api.example.test"),
    )

    assert type(error) is NetworkError
    assert str(error) == "HTTP transport failed"
    assert repr(error) == "NetworkError('HTTP transport failed')"
    assert error.args == ("HTTP transport failed",)


def test_transport_mapper_builds_safe_request_only_context_and_preserves_sources() -> None:
    headers = {"Authorization": "Bearer test-transport-secret", "X-Request-ID": "safe-id"}
    url = "https://example.test/items?token=test-query-secret&safe=visible"
    request = RequestContext("GET", url, headers=headers)

    error = _transport_error_from_httpx(httpx.ConnectError("detail"), request, attempt=3)

    assert error.context == {
        "method": "GET",
        "url": "https://example.test/items?token=<redacted>&safe=visible",
        "request_headers": {"authorization": "<redacted>", "x-request-id": "safe-id"},
        "attempt": 3,
    }
    assert not {"status_code", "response_headers", "body_snippet", "payload"} & set(error.context)
    assert "test-transport-secret" not in repr(error.context)
    assert "test-query-secret" not in repr(error.context)
    assert request.url == url
    assert headers == {"Authorization": "Bearer test-transport-secret", "X-Request-ID": "safe-id"}
