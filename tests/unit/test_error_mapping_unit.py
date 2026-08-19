from __future__ import annotations

import httpx
import pytest
from api_client_kit.client.models import RequestContext, ResponseData
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
from api_client_kit.errors.mapping import _http_error_for_response

pytestmark = [pytest.mark.unit]


@pytest.mark.parametrize(
    ("status_code", "error_type"),
    [
        (401, AuthenticationError),
        (403, AuthorizationError),
        (404, NotFoundError),
        (409, ConflictError),
        (422, ValidationError),
        (429, RateLimitError),
    ],
)
def test_explicit_statuses_construct_specialized_errors(
    status_code: int, error_type: type[HttpStatusError]
) -> None:
    response = ResponseData(raw=httpx.Response(status_code))
    request = RequestContext(method="GET", url="https://api.example.test/items")

    error = _http_error_for_response(response, request)

    assert error is not None
    assert type(error) is error_type
    assert isinstance(error, HttpStatusError)
    assert isinstance(error, ApiClientError)
    assert error.response is response
    assert str(error) == f"HTTP request failed with status {status_code}"
    assert error.context is not None


@pytest.mark.parametrize("status_code", [500, 502, 503, 599])
def test_server_statuses_construct_server_errors(status_code: int) -> None:
    error = _http_error_for_response(
        ResponseData(raw=httpx.Response(status_code)),
        RequestContext(method="GET", url="https://api.example.test/items"),
    )

    assert error is not None
    assert type(error) is ServerError


@pytest.mark.parametrize(
    ("status_code", "error_type"),
    [(499, HttpStatusError), (500, ServerError), (599, ServerError), (600, HttpStatusError)],
)
def test_server_status_range_boundaries(
    status_code: int, error_type: type[HttpStatusError]
) -> None:
    error = _http_error_for_response(
        ResponseData(raw=httpx.Response(status_code)),
        RequestContext(method="GET", url="https://api.example.test/items"),
    )

    assert error is not None
    assert type(error) is error_type


@pytest.mark.parametrize("status_code", [400, 418])
def test_generic_client_error_statuses_construct_exact_base_error(status_code: int) -> None:
    error = _http_error_for_response(
        ResponseData(raw=httpx.Response(status_code)),
        RequestContext(method="GET", url="https://api.example.test/items"),
    )

    assert error is not None
    assert type(error) is HttpStatusError


@pytest.mark.parametrize("status_code", [200, 204, 301, 302, 399])
def test_non_error_statuses_return_none_without_constructing_context(
    monkeypatch: pytest.MonkeyPatch, status_code: int
) -> None:
    def fail_if_called(*args: object, **kwargs: object) -> dict[str, object]:
        msg = "context should not be built for non-error responses"
        raise AssertionError(msg)

    monkeypatch.setattr("api_client_kit.errors.mapping._build_error_context", fail_if_called)

    assert (
        _http_error_for_response(
            ResponseData(raw=httpx.Response(status_code)),
            RequestContext(method="GET", url="https://api.example.test/items"),
        )
        is None
    )


@pytest.mark.parametrize("status_code", [401, 418, 500])
def test_messages_are_exact_and_exclude_server_controlled_content(status_code: int) -> None:
    fake_server_value = "test-server-secret"
    raw_response = httpx.Response(status_code, json={"message": fake_server_value})
    response = ResponseData(raw=raw_response)

    error = _http_error_for_response(
        response, RequestContext(method="GET", url="https://api.example.test/items")
    )

    assert error is not None
    assert str(error) == f"HTTP request failed with status {status_code}"
    assert fake_server_value not in str(error)
    assert fake_server_value not in repr(error)
    assert error.response.raw is raw_response


def test_mapping_composes_safe_context_and_propagates_attempt() -> None:
    fake_request_value = "test-request-secret"
    fake_query_value = "test-query-secret"
    raw_response = httpx.Response(
        401,
        headers={"Content-Type": "application/json"},
        json={
            "received": f"Bearer {fake_request_value} {fake_query_value}",
            "token": "test-body-secret",
        },
    )
    response = ResponseData(raw=raw_response)

    error = _http_error_for_response(
        response,
        RequestContext(
            method="GET",
            url=f"https://api.example.test/items?token={fake_query_value}",
            headers={"Authorization": f"Bearer {fake_request_value}"},
        ),
        attempt=3,
    )

    assert error is not None
    assert error.response is response
    assert error.response.raw is raw_response
    context = error.context
    assert context is not None
    assert context["attempt"] == 3
    assert context["status_code"] == 401
    assert context["payload"] == {"received": "<redacted> <redacted>", "token": "<redacted>"}
    rendered = repr(context)
    assert fake_request_value not in rendered
    assert fake_query_value not in rendered
    assert "test-body-secret" not in rendered
