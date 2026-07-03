from __future__ import annotations

import httpx
import pytest
from api_client_kit.client.headers import merge_headers

pytestmark = [pytest.mark.unit]


def test_merge_headers_imports_from_client_headers() -> None:
    assert merge_headers.__name__ == "merge_headers"


def test_merge_headers_is_in_headers_all() -> None:
    import api_client_kit.client.headers as headers

    assert "merge_headers" in headers.__all__
    assert headers.__all__ == ("merge_headers",)


def test_merge_headers_none_inputs_return_empty_headers() -> None:
    merged = merge_headers()

    assert isinstance(merged, httpx.Headers)
    assert merged == httpx.Headers()


def test_merge_headers_default_headers_only() -> None:
    merged = merge_headers({"User-Agent": "api-client-kit", "Accept": "application/json"})

    assert merged["User-Agent"] == "api-client-kit"
    assert merged["Accept"] == "application/json"


def test_merge_headers_request_headers_only() -> None:
    merged = merge_headers(request_headers={"X-Request-ID": "abc"})

    assert merged["X-Request-ID"] == "abc"


def test_merge_headers_adds_request_headers_to_defaults() -> None:
    merged = merge_headers(
        {"User-Agent": "api-client-kit", "Accept": "application/json"},
        {"X-Request-ID": "abc"},
    )

    assert merged["User-Agent"] == "api-client-kit"
    assert merged["Accept"] == "application/json"
    assert merged["X-Request-ID"] == "abc"


def test_merge_headers_request_headers_override_default_headers() -> None:
    merged = merge_headers(
        {"Authorization": "Bearer default-token"},
        {"Authorization": "Bearer request-token"},
    )

    assert merged["Authorization"] == "Bearer request-token"


def test_merge_headers_case_insensitive_request_headers_override_defaults() -> None:
    merged = merge_headers(
        {"Authorization": "Bearer default-token"},
        {"authorization": "Bearer request-token"},
    )

    assert merged["Authorization"] == "Bearer request-token"
    assert merged["authorization"] == "Bearer request-token"


def test_merge_headers_case_insensitive_override_has_one_logical_header() -> None:
    merged = merge_headers(
        {"Authorization": "Bearer default-token"},
        {"authorization": "Bearer request-token"},
    )

    authorization_items = [
        (name, value) for name, value in merged.multi_items() if name.lower() == "authorization"
    ]

    assert authorization_items == [("authorization", "Bearer request-token")]


def test_merge_headers_does_not_mutate_input_dictionaries() -> None:
    default_headers = {"Authorization": "Bearer default-token"}
    request_headers = {"authorization": "Bearer request-token"}

    merge_headers(default_headers, request_headers)

    assert default_headers == {"Authorization": "Bearer default-token"}
    assert request_headers == {"authorization": "Bearer request-token"}


def test_merge_headers_does_not_mutate_input_httpx_headers() -> None:
    default_headers = httpx.Headers({"Authorization": "Bearer default-token"})
    request_headers = httpx.Headers({"authorization": "Bearer request-token"})

    merge_headers(default_headers, request_headers)

    assert default_headers["Authorization"] == "Bearer default-token"
    assert default_headers.multi_items() == [("authorization", "Bearer default-token")]
    assert request_headers["Authorization"] == "Bearer request-token"
    assert request_headers.multi_items() == [("authorization", "Bearer request-token")]


def test_merge_headers_returns_new_httpx_headers_object() -> None:
    default_headers = httpx.Headers({"User-Agent": "api-client-kit"})
    request_headers = httpx.Headers({"X-Request-ID": "abc"})

    merged = merge_headers(default_headers, request_headers)

    assert isinstance(merged, httpx.Headers)
    assert merged is not default_headers
    assert merged is not request_headers


def test_merge_headers_is_not_exported_from_client_package() -> None:
    import api_client_kit.client as client

    assert not hasattr(client, "merge_headers")


def test_merge_headers_is_not_exported_from_top_level_package() -> None:
    import api_client_kit

    assert not hasattr(api_client_kit, "merge_headers")
