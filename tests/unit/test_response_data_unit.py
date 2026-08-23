from __future__ import annotations

import json
from dataclasses import FrozenInstanceError

import httpx
import pytest
from api_client_kit.client.models import ResponseData
from api_client_kit.errors import DecodeError

pytestmark = [pytest.mark.unit]


def test_response_data_imports_from_client_models() -> None:
    assert ResponseData.__name__ == "ResponseData"


def test_response_data_exposes_raw_response() -> None:
    response = httpx.Response(204)

    data = ResponseData(raw=response)

    assert data.raw is response


def test_response_data_exposes_status_code() -> None:
    data = ResponseData(raw=httpx.Response(201))

    assert data.status_code == 201


def test_response_data_exposes_headers() -> None:
    response = httpx.Response(200, headers={"X-Test": "true"})

    data = ResponseData(raw=response)

    assert data.headers is response.headers
    assert data.headers["X-Test"] == "true"


def test_response_data_exposes_text() -> None:
    data = ResponseData(raw=httpx.Response(200, text="hello"))

    assert data.text == "hello"


def test_response_data_exposes_content() -> None:
    data = ResponseData(raw=httpx.Response(200, content=b"raw-body"))

    assert data.content == b"raw-body"


@pytest.mark.parametrize(
    ("body", "expected"),
    [(b'{"value": 1}', {"value": 1}), (b"[1, 2]", [1, 2]), (b"42", 42), (b"null", None)],
)
def test_response_data_json_returns_all_valid_json_shapes(body: bytes, expected: object) -> None:
    data = ResponseData(raw=httpx.Response(200, content=body))

    assert data.json() == expected


@pytest.mark.parametrize("headers", [{"Content-Type": "text/plain"}, {}])
def test_response_data_json_is_not_content_type_gated(headers: dict[str, str]) -> None:
    data = ResponseData(raw=httpx.Response(200, headers=headers, content=b'{"ok": true}'))

    assert data.json() == {"ok": True}


def test_response_data_json_does_not_redact_successful_data() -> None:
    data = ResponseData(
        raw=httpx.Response(
            200,
            json={"token": "actual-api-value", "password": "actual-response-value"},
        )
    )

    assert data.json() == {"token": "actual-api-value", "password": "actual-response-value"}


def test_response_data_json_is_independent_of_http_status() -> None:
    data = ResponseData(raw=httpx.Response(404, content=b'{"error": "missing"}'))

    assert data.json() == {"error": "missing"}


def test_response_data_json_translates_malformed_json_with_identity_and_cause() -> None:
    raw_response = httpx.Response(200, content=b'{"value":')
    data = ResponseData(raw=raw_response)

    with pytest.raises(DecodeError) as exc_info:
        data.json()

    error = exc_info.value
    assert str(error) == "Failed to decode response as JSON"
    assert repr(error) == "DecodeError('Failed to decode response as JSON')"
    assert error.args == ("Failed to decode response as JSON",)
    assert error.response is data
    assert error.response.raw is raw_response
    assert isinstance(error.__cause__, json.JSONDecodeError)
    assert error.context == {
        "status_code": 200,
        "content_type": None,
        "body_snippet": '{"value":',
    }


@pytest.mark.parametrize(
    ("headers", "body"),
    [
        ({}, b""),
        ({"Content-Type": "application/json"}, b"hello"),
        ({"Content-Type": "text/plain"}, b"hello"),
    ],
)
def test_response_data_json_translates_invalid_content_independently_of_content_type(
    headers: dict[str, str], body: bytes
) -> None:
    data = ResponseData(raw=httpx.Response(200, headers=headers, content=body))

    with pytest.raises(DecodeError) as exc_info:
        data.json()

    assert exc_info.value.context["body_snippet"] == ("<empty>" if not body else "hello")


def test_response_data_json_uses_attached_request_for_safe_decode_diagnostics() -> None:
    request = httpx.Request(
        "POST",
        "https://test-user:test-password@example.test/items?token=test-query-secret&safe=visible#fragment",
        headers={"Authorization": "Bearer test-header-secret"},
    )
    data = ResponseData(
        raw=httpx.Response(
            400,
            headers={"Content-Type": "text/html"},
            content=b"not-json Bearer test-header-secret test-query-secret test-user test-password",
            request=request,
        )
    )

    with pytest.raises(DecodeError) as exc_info:
        data.json()

    context = exc_info.value.context
    assert set(context) == {"method", "url", "status_code", "content_type", "body_snippet"}
    assert context["method"] == "POST"
    assert context["content_type"] == "text/html"
    assert context["url"] == (
        "https://<redacted>:<redacted>@example.test/items?token=<redacted>&safe=visible"
    )
    rendered = repr(context)
    for secret in ("test-user", "test-password", "test-query-secret", "test-header-secret"):
        assert secret not in rendered
    assert "<redacted>" in str(context["body_snippet"])


def test_response_data_json_bounds_large_failed_body_diagnostics() -> None:
    body = b"x" * 2_000
    data = ResponseData(raw=httpx.Response(200, content=body))

    with pytest.raises(DecodeError) as exc_info:
        data.json()

    snippet = exc_info.value.context["body_snippet"]
    assert isinstance(snippet, str)
    assert snippet.endswith("…<truncated>")
    assert snippet != body.decode()


def test_response_data_json_delegates_to_raw_response() -> None:
    data = ResponseData(raw=httpx.Response(200, json={"ok": True}))

    assert data.json() == {"ok": True}


def test_response_data_is_frozen() -> None:
    data = ResponseData(raw=httpx.Response(200))

    with pytest.raises(FrozenInstanceError):
        data.raw = httpx.Response(201)


def test_response_data_uses_slots_without_instance_dict() -> None:
    data = ResponseData(raw=httpx.Response(200))

    assert not hasattr(data, "__dict__")


def test_response_data_is_in_models_all() -> None:
    import api_client_kit.client.models as models

    assert "ResponseData" in models.__all__
    assert models.__all__ == ("RequestOptions", "ResponseData")


def test_request_context_remains_excluded_from_models_all() -> None:
    import api_client_kit.client.models as models

    assert "RequestContext" not in models.__all__


def test_response_data_is_exported_from_client_package() -> None:
    import api_client_kit.client as client

    assert client.ResponseData is ResponseData


def test_response_data_is_exported_from_top_level_package() -> None:
    import api_client_kit

    assert api_client_kit.ResponseData is ResponseData
