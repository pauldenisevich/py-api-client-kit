from __future__ import annotations

import inspect
import json as jsonlib
from typing import Any

import httpx
import pytest
from api_client_kit.client.async_client import AsyncClient
from api_client_kit.client.models import ResponseData

pytestmark = [pytest.mark.integration]


@pytest.mark.asyncio
async def test_async_client_request_exists() -> None:
    assert callable(AsyncClient.request)


@pytest.mark.asyncio
async def test_get_request_reaches_expected_url() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = AsyncClient(
        base_url="https://api.example.test/v1",
        transport=httpx.MockTransport(handler),
    )

    await client.request("GET", "users")

    assert str(requests[0].url) == "https://api.example.test/v1/users"


@pytest.mark.asyncio
async def test_base_url_prefix_is_preserved_when_path_starts_with_slash() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = AsyncClient(
        base_url="https://api.example.test/api/v1",
        transport=httpx.MockTransport(handler),
    )

    await client.request("GET", "/users")

    assert str(requests[0].url) == "https://api.example.test/api/v1/users"


@pytest.mark.asyncio
async def test_method_is_normalized_to_uppercase() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    await client.request("post", "/users")

    assert requests[0].method == "POST"


@pytest.mark.asyncio
async def test_params_pass_through() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    await client.request("GET", "/users", params={"limit": 10, "active": "true"})

    assert requests[0].url.params["limit"] == "10"
    assert requests[0].url.params["active"] == "true"


@pytest.mark.asyncio
async def test_headers_pass_through() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    await client.request("GET", "/users", headers={"X-Request-ID": "abc"})

    assert requests[0].headers["X-Request-ID"] == "abc"


@pytest.mark.asyncio
async def test_default_headers_merge_with_request_headers() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = AsyncClient(
        base_url="https://api.example.test",
        headers={"User-Agent": "api-client-kit"},
        transport=httpx.MockTransport(handler),
    )

    await client.request("GET", "/users", headers={"X-Request-ID": "abc"})

    assert requests[0].headers["User-Agent"] == "api-client-kit"
    assert requests[0].headers["X-Request-ID"] == "abc"


@pytest.mark.asyncio
async def test_request_headers_override_default_headers() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = AsyncClient(
        base_url="https://api.example.test",
        headers={"Authorization": "Bearer default-token"},
        transport=httpx.MockTransport(handler),
    )

    await client.request("GET", "/users", headers={"authorization": "Bearer request-token"})

    assert requests[0].headers["Authorization"] == "Bearer request-token"


@pytest.mark.asyncio
async def test_response_is_wrapped_in_response_data_and_raw_response_access_works() -> None:
    raw_response = httpx.Response(202, text="accepted")

    async def handler(request: httpx.Request) -> httpx.Response:
        return raw_response

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    response = await client.request("GET", "/jobs/1")

    assert isinstance(response, ResponseData)
    assert response.raw is raw_response
    assert response.status_code == 202
    assert response.text == "accepted"


@pytest.mark.asyncio
async def test_json_response_happy_path_works() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    response = await client.request("GET", "/status")

    assert response.json() == {"ok": True}


@pytest.mark.asyncio
async def test_non_2xx_response_returns_response_data_without_raising_status_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": "nope"})

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    response = await client.request("GET", "/missing")

    assert isinstance(response, ResponseData)
    assert response.status_code == 404
    assert response.json() == {"error": "nope"}


@pytest.mark.asyncio
async def test_post_style_json_body_passes_through() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(201, json={"created": True})

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    await client.request("POST", "/users", json={"name": "Ada"})

    assert jsonlib.loads(requests[0].content) == {"name": "Ada"}


@pytest.mark.asyncio
async def test_data_body_passes_through() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(201)

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    await client.request("POST", "/uploads", data={"name": "Ada"})

    assert requests[0].content == b"name=Ada"


@pytest.mark.asyncio
async def test_client_default_timeout_is_used_when_request_timeout_is_omitted() -> None:
    captured_timeouts: list[Any] = []
    client = AsyncClient(base_url="https://api.example.test", timeout=7.5)

    async def request_spy(**kwargs: Any) -> httpx.Response:
        captured_timeouts.append(kwargs["timeout"])
        return httpx.Response(200)

    client._client.request = request_spy  # type: ignore[method-assign]

    await client.request("GET", "/users")

    assert captured_timeouts == [7.5]


@pytest.mark.asyncio
async def test_per_request_float_timeout_overrides_client_default_timeout() -> None:
    captured_timeouts: list[Any] = []
    client = AsyncClient(base_url="https://api.example.test", timeout=7.5)

    async def request_spy(**kwargs: Any) -> httpx.Response:
        captured_timeouts.append(kwargs["timeout"])
        return httpx.Response(200)

    client._client.request = request_spy  # type: ignore[method-assign]

    await client.request("GET", "/users", timeout=1.25)

    assert captured_timeouts == [1.25]


@pytest.mark.asyncio
async def test_per_request_httpx_timeout_overrides_client_default_timeout() -> None:
    captured_timeouts: list[Any] = []
    client = AsyncClient(base_url="https://api.example.test", timeout=7.5)
    timeout = httpx.Timeout(2.0)

    async def request_spy(**kwargs: Any) -> httpx.Response:
        captured_timeouts.append(kwargs["timeout"])
        return httpx.Response(200)

    client._client.request = request_spy  # type: ignore[method-assign]

    await client.request("GET", "/users", timeout=timeout)

    assert captured_timeouts == [timeout]
    assert captured_timeouts[0] is timeout


@pytest.mark.asyncio
async def test_explicit_timeout_none_overrides_client_default_timeout() -> None:
    captured_timeouts: list[Any] = []
    client = AsyncClient(base_url="https://api.example.test", timeout=7.5)

    async def request_spy(**kwargs: Any) -> httpx.Response:
        captured_timeouts.append(kwargs["timeout"])
        return httpx.Response(200)

    client._client.request = request_spy  # type: ignore[method-assign]

    await client.request("GET", "/users", timeout=None)

    assert captured_timeouts == [None]


@pytest.mark.asyncio
async def test_idempotency_key_does_not_automatically_add_header() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    await client.request("POST", "/users", idempotency_key="request-123")

    assert "Idempotency-Key" not in requests[0].headers


@pytest.mark.asyncio
async def test_tags_do_not_create_request_behavior() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    response = await client.request("GET", "/users", tags=("users", "read"))

    assert response.status_code == 200
    assert str(requests[0].url) == "https://api.example.test/users"
    assert "tags" not in requests[0].headers


@pytest.mark.asyncio
async def test_async_client_still_has_no_convenience_methods() -> None:
    convenience_methods: tuple[str, ...] = ("get", "post", "put", "patch", "delete", "head")

    for name in convenience_methods:
        assert not hasattr(AsyncClient, name)


@pytest.mark.asyncio
async def test_async_client_still_has_no_aclose_method() -> None:
    assert not hasattr(AsyncClient, "aclose")


@pytest.mark.asyncio
async def test_async_client_still_has_no_async_context_manager_behavior() -> None:
    assert not hasattr(AsyncClient, "__aenter__")
    assert not hasattr(AsyncClient, "__aexit__")


@pytest.mark.asyncio
async def test_no_auth_retry_rate_limit_or_hooks_placeholder_parameters_exist() -> None:
    parameters = inspect.signature(AsyncClient.request).parameters

    assert "auth" not in parameters
    assert "retry_policy" not in parameters
    assert "rate_limiter" not in parameters
    assert "hooks" not in parameters
