from __future__ import annotations

import httpx
import pytest
from api_client_kit.client.models import RequestContext
from api_client_kit.errors.context import _build_error_context

pytestmark = [pytest.mark.unit]


def test_request_only_context_has_exact_safe_schema_and_attempt() -> None:
    request = RequestContext(
        method="get",
        url="https://user:test-url-password@example.test/items?token=test-query-secret&safe=visible#x",
        headers={"Authorization": "Bearer test-request-secret", "X-Test-Safe": "visible"},
    )

    context = _build_error_context(request)

    assert set(context) == {"method", "url", "request_headers", "attempt"}
    assert context["method"] == "GET"
    assert context["attempt"] == 1
    assert (
        context["url"]
        == "https://<redacted>:<redacted>@example.test/items?token=<redacted>&safe=visible"
    )
    assert context["request_headers"] == {"authorization": "<redacted>", "x-test-safe": "visible"}
    assert _build_error_context(request, attempt=3)["attempt"] == 3


def test_response_context_scrubs_headers_payload_and_echoed_request_secrets() -> None:
    request = RequestContext(
        method="POST",
        url="https://test-user:test-url-password@example.test/?token=test-query-secret",
        headers={"Authorization": "Bearer test-request-secret", "Cookie": "test-cookie-secret"},
    )
    response = httpx.Response(
        401,
        headers={
            "Content-Type": "application/problem+json",
            "Set-Cookie": "test-response-secret",
            "X-Test-Safe": "yes",
        },
        json={
            "error": "bad request",
            "password": "test-payload-secret",
            "received": "Bearer test-request-secret test-query-secret test-user test-url-password",
            "nested": {"token": "test-nested-secret"},
        },
    )

    context = _build_error_context(request, response=response)

    assert set(context) == {
        "method",
        "url",
        "request_headers",
        "attempt",
        "status_code",
        "response_headers",
        "body_snippet",
        "payload",
    }
    assert context["status_code"] == 401
    response_headers = context["response_headers"]
    assert isinstance(response_headers, dict)
    assert response_headers["content-type"] == "application/problem+json"
    assert response_headers["set-cookie"] == "<redacted>"
    assert response_headers["x-test-safe"] == "yes"
    assert context["payload"] == {
        "error": "bad request",
        "password": "<redacted>",
        "received": "<redacted> <redacted> <redacted> <redacted>",
        "nested": {"token": "<redacted>"},
    }
    rendered = repr(context)
    for secret in (
        "test-request-secret",
        "test-query-secret",
        "test-url-password",
        "test-user",
        "test-cookie-secret",
        "test-response-secret",
        "test-payload-secret",
        "test-nested-secret",
    ):
        assert secret not in rendered


@pytest.mark.parametrize(
    "content_type", ["application/json; charset=utf-8", "Application/Vnd.Example+Json"]
)
def test_json_media_types_create_payload(content_type: str) -> None:
    context = _build_error_context(
        RequestContext(method="GET", url="/items"),
        response=httpx.Response(400, headers={"Content-Type": content_type}, json=["safe", 1]),
    )

    assert context["payload"] == ["safe", 1]


def test_empty_malformed_non_json_binary_and_large_bodies_are_safe() -> None:
    request = RequestContext(method="GET", url="/items")
    empty = _build_error_context(request, response=httpx.Response(204, content=b""))
    malformed = _build_error_context(
        request,
        response=httpx.Response(
            400, headers={"Content-Type": "application/json"}, content=b'{"error":'
        ),
    )
    non_json = _build_error_context(
        request,
        response=httpx.Response(
            400, headers={"Content-Type": "text/plain"}, content=b'{"error":"safe"}'
        ),
    )
    binary = _build_error_context(
        request,
        response=httpx.Response(
            400, headers={"Content-Type": "application/json"}, content=b"\xff\xfe"
        ),
    )
    large = _build_error_context(
        request,
        response=httpx.Response(
            400,
            headers={"Content-Type": "application/json"},
            content=(b'{"safe":"' + b"a" * 2000 + b'"}'),
        ),
    )

    assert empty["body_snippet"] == "<empty>"
    assert "payload" not in empty
    assert malformed["body_snippet"] == '{"error":'
    assert "payload" not in malformed
    assert non_json["body_snippet"] == '{"error":"safe"}'
    assert "payload" not in non_json
    assert binary["body_snippet"] == "<binary body: 2 bytes>"
    assert "payload" not in binary
    assert str(large["body_snippet"]).endswith("…<truncated>")
    assert "payload" not in large


def test_sources_are_unchanged_and_context_retains_only_builtin_diagnostics() -> None:
    headers = {"Authorization": "test-secret", "X-Safe": "yes"}
    request = RequestContext(
        method="GET", url="https://example.test/?token=test-query", headers=headers
    )
    response = httpx.Response(400, headers={"Authorization": "response-secret"}, text="test-secret")
    original_request_headers = dict(headers)
    original_response_headers = dict(response.headers)

    context = _build_error_context(request, response=response)

    assert headers == original_request_headers
    assert dict(response.headers) == original_response_headers
    assert all(
        not isinstance(value, (httpx.Headers, httpx.Response, RequestContext))
        for value in context.values()
    )
