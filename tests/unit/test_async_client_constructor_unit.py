from __future__ import annotations

from typing import Any

import httpx
import pytest
from api_client_kit.client.async_client import AsyncClient

pytestmark = [pytest.mark.unit]


class RecordingAsyncTransport(httpx.AsyncBaseTransport):
    def __init__(self) -> None:
        self.calls = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.calls += 1
        return httpx.Response(200)


def test_async_client_imports_from_async_client_module() -> None:
    assert AsyncClient.__name__ == "AsyncClient"


def test_async_client_is_in_async_client_all() -> None:
    import api_client_kit.client.async_client as async_client

    assert "AsyncClient" in async_client.__all__
    assert async_client.__all__ == ("AsyncClient",)


def test_async_client_requires_keyword_only_base_url() -> None:
    with pytest.raises(TypeError, match=r"missing .* required keyword-only argument"):
        AsyncClient()

    with pytest.raises(TypeError, match="positional"):
        AsyncClient("https://api.example.test")  # type: ignore[misc]


def test_async_client_stores_canonical_base_url() -> None:
    client = AsyncClient(base_url="https://api.example.test/v1/")

    assert client.base_url == "https://api.example.test/v1"


def test_async_client_rejects_invalid_base_url_through_url_validation() -> None:
    with pytest.raises(ValueError, match="base_url must be an absolute HTTP or HTTPS URL"):
        AsyncClient(base_url="/v1")


def test_async_client_stores_default_headers_as_httpx_headers() -> None:
    client = AsyncClient(
        base_url="https://api.example.test",
        headers={"User-Agent": "api-client-kit"},
    )

    assert isinstance(client._default_headers, httpx.Headers)
    assert client.default_headers["User-Agent"] == "api-client-kit"


def test_async_client_default_headers_are_case_insensitive() -> None:
    client = AsyncClient(
        base_url="https://api.example.test",
        headers={"Authorization": "Bearer test-token"},
    )

    assert client.default_headers["Authorization"] == "Bearer test-token"
    assert client.default_headers["authorization"] == "Bearer test-token"


def test_async_client_copies_input_headers() -> None:
    headers = {"X-Test": "before"}

    client = AsyncClient(base_url="https://api.example.test", headers=headers)
    headers["X-Test"] = "after"

    assert client.default_headers["X-Test"] == "before"


def test_async_client_default_headers_property_returns_copy() -> None:
    client = AsyncClient(
        base_url="https://api.example.test",
        headers={"X-Test": "before"},
    )

    headers = client.default_headers
    headers["X-Test"] = "after"

    assert headers["X-Test"] == "after"
    assert client.default_headers["X-Test"] == "before"
    assert client.default_headers is not client._default_headers


def test_async_client_stores_default_timeout_float() -> None:
    client = AsyncClient(base_url="https://api.example.test", timeout=3.5)

    assert client.timeout == 3.5


def test_async_client_accepts_and_stores_httpx_timeout_by_identity() -> None:
    timeout = httpx.Timeout(5.0)

    client = AsyncClient(base_url="https://api.example.test", timeout=timeout)

    assert client.timeout is timeout


def test_async_client_accepts_and_stores_timeout_none() -> None:
    client = AsyncClient(base_url="https://api.example.test", timeout=None)

    assert client.timeout is None


def test_async_client_stores_injected_async_transport() -> None:
    transport = RecordingAsyncTransport()

    client = AsyncClient(base_url="https://api.example.test", transport=transport)

    assert client._transport is transport


def test_async_client_raise_for_status_defaults_to_true() -> None:
    client = AsyncClient(base_url="https://api.example.test")

    assert client.raise_for_status is True


@pytest.mark.parametrize("value", [True, False])
def test_async_client_stores_explicit_raise_for_status(value: bool) -> None:
    client = AsyncClient(base_url="https://api.example.test", raise_for_status=value)

    assert client.raise_for_status is value


@pytest.mark.parametrize("value", [None, 0, 1, "false"])
def test_async_client_rejects_non_bool_raise_for_status(value: object) -> None:
    with pytest.raises(TypeError, match=r"^raise_for_status must be bool$"):
        AsyncClient(base_url="https://api.example.test", raise_for_status=value)  # type: ignore[arg-type]


def test_async_client_raise_for_status_is_read_only() -> None:
    client = AsyncClient(base_url="https://api.example.test")

    with pytest.raises(AttributeError):
        client.raise_for_status = False  # type: ignore[misc]


def test_async_client_creates_internal_httpx_async_client() -> None:
    client = AsyncClient(base_url="https://api.example.test")

    assert isinstance(client._client, httpx.AsyncClient)


def test_async_client_constructor_does_not_send_requests() -> None:
    transport = RecordingAsyncTransport()

    client = AsyncClient(base_url="https://api.example.test", transport=transport)

    assert client._transport is transport
    assert isinstance(client._client, httpx.AsyncClient)
    assert transport.calls == 0


def test_async_client_does_not_configure_httpx_async_client_base_url_headers_or_timeout() -> None:
    timeout = httpx.Timeout(2.0)
    client = AsyncClient(
        base_url="https://api.example.test/v1",
        headers={"X-Test": "true"},
        timeout=timeout,
    )

    assert str(client._client.base_url) == ""
    assert "X-Test" not in client._client.headers
    assert client._client.timeout is not timeout


def test_async_client_is_exported_from_client_package() -> None:
    import api_client_kit.client as client

    assert client.AsyncClient is AsyncClient


def test_async_client_is_exported_from_top_level_package() -> None:
    import api_client_kit

    assert api_client_kit.AsyncClient is AsyncClient


def test_async_client_has_convenience_methods() -> None:
    convenience_methods: tuple[str, ...] = ("get", "post", "put", "patch", "delete", "head")

    assert all(callable(getattr(AsyncClient, name)) for name in convenience_methods)


def test_async_client_has_async_lifecycle_methods() -> None:
    lifecycle_methods: tuple[str, ...] = (
        "aclose",
        "__aenter__",
        "__aexit__",
    )

    assert all(callable(getattr(AsyncClient, name)) for name in lifecycle_methods)


def test_async_client_constructor_has_no_future_placeholder_parameters() -> None:
    with pytest.raises(TypeError, match="unexpected keyword argument"):
        AsyncClient(base_url="https://api.example.test", auth=object())  # type: ignore[call-arg]

    unexpected_kwargs: dict[str, Any] = {
        "retry_policy": object(),
        "rate_limiter": object(),
        "hooks": (),
    }

    for name, value in unexpected_kwargs.items():
        with pytest.raises(TypeError, match="unexpected keyword argument"):
            AsyncClient(base_url="https://api.example.test", **{name: value})  # type: ignore[arg-type]
