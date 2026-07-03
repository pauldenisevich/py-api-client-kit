from __future__ import annotations

from typing import Any

import httpx
import pytest
from api_client_kit.client.sync_client import SyncClient

pytestmark = [pytest.mark.unit]


def test_sync_client_imports_from_sync_client_module() -> None:
    assert SyncClient.__name__ == "SyncClient"


def test_sync_client_is_in_sync_client_all() -> None:
    import api_client_kit.client.sync_client as sync_client

    assert "SyncClient" in sync_client.__all__
    assert sync_client.__all__ == ("SyncClient",)


def test_sync_client_requires_keyword_only_base_url() -> None:
    with pytest.raises(TypeError, match=r"missing .* required keyword-only argument"):
        SyncClient()

    with pytest.raises(TypeError, match="positional"):
        SyncClient("https://api.example.test")  # type: ignore[misc]


def test_sync_client_stores_canonical_base_url() -> None:
    client = SyncClient(base_url="https://api.example.test/v1/")

    assert client.base_url == "https://api.example.test/v1"


def test_sync_client_rejects_invalid_base_url_through_url_validation() -> None:
    with pytest.raises(ValueError, match="base_url must be an absolute HTTP or HTTPS URL"):
        SyncClient(base_url="/v1")


def test_sync_client_stores_default_headers_as_httpx_headers() -> None:
    client = SyncClient(
        base_url="https://api.example.test",
        headers={"User-Agent": "api-client-kit"},
    )

    assert isinstance(client._default_headers, httpx.Headers)
    assert client.default_headers["User-Agent"] == "api-client-kit"


def test_sync_client_default_headers_are_case_insensitive() -> None:
    client = SyncClient(
        base_url="https://api.example.test",
        headers={"Authorization": "Bearer test-token"},
    )

    assert client.default_headers["Authorization"] == "Bearer test-token"
    assert client.default_headers["authorization"] == "Bearer test-token"


def test_sync_client_copies_input_headers() -> None:
    headers = {"X-Test": "before"}

    client = SyncClient(base_url="https://api.example.test", headers=headers)
    headers["X-Test"] = "after"

    assert client.default_headers["X-Test"] == "before"


def test_sync_client_default_headers_property_returns_copy() -> None:
    client = SyncClient(
        base_url="https://api.example.test",
        headers={"X-Test": "before"},
    )

    headers = client.default_headers
    headers["X-Test"] = "after"

    assert headers["X-Test"] == "after"
    assert client.default_headers["X-Test"] == "before"
    assert client.default_headers is not client._default_headers


def test_sync_client_stores_default_timeout_float() -> None:
    client = SyncClient(base_url="https://api.example.test", timeout=3.5)

    assert client.timeout == 3.5


def test_sync_client_accepts_and_stores_httpx_timeout_by_identity() -> None:
    timeout = httpx.Timeout(5.0)

    client = SyncClient(base_url="https://api.example.test", timeout=timeout)

    assert client.timeout is timeout


def test_sync_client_accepts_and_stores_timeout_none() -> None:
    client = SyncClient(base_url="https://api.example.test", timeout=None)

    assert client.timeout is None


def test_sync_client_stores_injected_transport() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200))

    client = SyncClient(base_url="https://api.example.test", transport=transport)

    assert client._transport is transport


def test_sync_client_creates_internal_httpx_client() -> None:
    client = SyncClient(base_url="https://api.example.test")

    assert isinstance(client._client, httpx.Client)


def test_sync_client_constructor_does_not_send_requests() -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200)

    SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    assert calls == []


def test_sync_client_does_not_configure_httpx_client_base_url_headers_or_timeout() -> None:
    timeout = httpx.Timeout(2.0)
    client = SyncClient(
        base_url="https://api.example.test/v1",
        headers={"X-Test": "true"},
        timeout=timeout,
    )

    assert str(client._client.base_url) == ""
    assert "X-Test" not in client._client.headers
    assert client._client.timeout is not timeout


def test_sync_client_is_not_exported_from_client_package() -> None:
    import api_client_kit.client as client

    assert not hasattr(client, "SyncClient")


def test_sync_client_is_not_exported_from_top_level_package() -> None:
    import api_client_kit

    assert not hasattr(api_client_kit, "SyncClient")


def test_sync_client_has_no_out_of_scope_runtime_methods() -> None:
    out_of_scope_methods: tuple[str, ...] = (
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "close",
        "__enter__",
        "__exit__",
    )

    assert all(not hasattr(SyncClient, name) for name in out_of_scope_methods)


def test_sync_client_constructor_has_no_future_placeholder_parameters() -> None:
    with pytest.raises(TypeError, match="unexpected keyword argument"):
        SyncClient(base_url="https://api.example.test", auth=object())  # type: ignore[call-arg]

    unexpected_kwargs: dict[str, Any] = {
        "retry_policy": object(),
        "rate_limiter": object(),
        "hooks": (),
    }

    for name, value in unexpected_kwargs.items():
        with pytest.raises(TypeError, match="unexpected keyword argument"):
            SyncClient(base_url="https://api.example.test", **{name: value})  # type: ignore[arg-type]
