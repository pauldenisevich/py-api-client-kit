from __future__ import annotations

import inspect
import json as jsonlib
from typing import Any

import httpx
import pytest
from api_client_kit.client.async_client import AsyncClient
from api_client_kit.client.models import ResponseData
from api_client_kit.errors import (
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

pytestmark = [pytest.mark.integration]


@pytest.mark.asyncio
async def test_async_client_maps_timeout_with_safe_request_context_and_cause() -> None:
    captured: list[httpx.TransportError] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        original = httpx.ReadTimeout("low-level timeout detail", request=request)
        captured.append(original)
        raise original

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(TimeoutError) as raised:
        await client.get(
            "/items?token=test-query-secret&page=2",
            headers={
                "Authorization": "Bearer test-async-transport-secret",
                "X-Request-ID": "safe-id",
            },
        )

    error = raised.value
    assert type(error) is TimeoutError
    assert str(error) == "HTTP request timed out"
    assert repr(error) == "TimeoutError('HTTP request timed out')"
    assert error.args == ("HTTP request timed out",)
    assert error.__cause__ is captured[0]
    assert error.context == {
        "method": "GET",
        "url": "https://api.example.test/items?token=<redacted>&page=2",
        "request_headers": {"authorization": "<redacted>", "x-request-id": "safe-id"},
        "attempt": 1,
    }
    assert not {"status_code", "response_headers", "body_snippet", "payload"} & set(error.context)
    for secret in (
        "test-query-secret",
        "test-async-transport-secret",
        "low-level timeout detail",
    ):
        assert secret not in str(error)
        assert secret not in repr(error)
        assert secret not in repr(error.context)


@pytest.mark.asyncio
async def test_async_client_maps_generic_transport_error_and_ignores_status_policy() -> None:
    captured: list[httpx.TransportError] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        original = httpx.ConnectError("low-level connection detail", request=request)
        captured.append(original)
        raise original

    client = AsyncClient(
        base_url="https://api.example.test",
        raise_for_status=False,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(NetworkError) as raised:
        await client.get("/items")

    error = raised.value
    assert type(error) is NetworkError
    assert str(error) == "HTTP transport failed"
    assert repr(error) == "NetworkError('HTTP transport failed')"
    assert error.args == ("HTTP transport failed",)
    assert error.__cause__ is captured[0]


@pytest.mark.asyncio
async def test_async_client_propagates_unrelated_transport_runtime_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        raise RuntimeError("test bug")

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(RuntimeError, match=r"^test bug$"):
        await client.get("/items")


@pytest.mark.asyncio
async def test_async_client_request_exists() -> None:
    assert callable(AsyncClient.request)


@pytest.mark.asyncio
async def test_async_client_convenience_methods_exist() -> None:
    convenience_methods: tuple[str, ...] = ("get", "post", "put", "patch", "delete", "head")

    assert all(callable(getattr(AsyncClient, name)) for name in convenience_methods)


@pytest.mark.asyncio
async def test_convenience_method_body_parameter_surface_matches_scope() -> None:
    body_capable_methods: tuple[str, ...] = ("post", "put", "patch")
    body_free_methods: tuple[str, ...] = ("get", "delete", "head")

    for name in body_capable_methods:
        parameters = inspect.signature(getattr(AsyncClient, name)).parameters
        assert "json" in parameters
        assert "data" in parameters

    for name in body_free_methods:
        parameters = inspect.signature(getattr(AsyncClient, name)).parameters
        assert "json" not in parameters
        assert "data" not in parameters


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method_name", "expected_method"),
    [
        ("get", "GET"),
        ("post", "POST"),
        ("put", "PUT"),
        ("patch", "PATCH"),
        ("delete", "DELETE"),
        ("head", "HEAD"),
    ],
)
async def test_convenience_methods_send_expected_http_method(
    method_name: str,
    expected_method: str,
) -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(204)

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    response = await getattr(client, method_name)("/resource")

    assert requests[0].method == expected_method
    assert isinstance(response, ResponseData)


@pytest.mark.asyncio
async def test_get_convenience_passes_params_and_headers() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    await client.get(
        "/users",
        params={"limit": 10, "active": "true"},
        headers={"X-Request-ID": "abc"},
    )

    assert requests[0].url.params["limit"] == "10"
    assert requests[0].url.params["active"] == "true"
    assert requests[0].headers["X-Request-ID"] == "abc"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method_name", "expected_method"),
    [
        ("post", "POST"),
        ("put", "PUT"),
        ("patch", "PATCH"),
    ],
)
async def test_body_capable_convenience_methods_pass_json_payload(
    method_name: str,
    expected_method: str,
) -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True})

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    response = await getattr(client, method_name)("/users", json={"name": "Ada"})

    assert requests[0].method == expected_method
    assert jsonlib.loads(requests[0].content) == {"name": "Ada"}
    assert response.json() == {"ok": True}


@pytest.mark.asyncio
async def test_post_convenience_passes_data_payload() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(201)

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    response = await client.post("/uploads", data={"name": "Ada"})

    assert isinstance(response, ResponseData)
    assert requests[0].method == "POST"
    assert requests[0].content == b"name=Ada"


@pytest.mark.asyncio
async def test_delete_convenience_sane_behavior() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(202, json={"deleted": True})

    client = AsyncClient(
        base_url="https://api.example.test/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = await client.delete(
        "/users/1",
        params={"force": "true"},
        headers={"X-Request-ID": "delete-1"},
    )

    assert isinstance(response, ResponseData)
    assert response.status_code == 202
    assert requests[0].method == "DELETE"
    assert str(requests[0].url) == "https://api.example.test/api/v1/users/1?force=true"
    assert requests[0].headers["X-Request-ID"] == "delete-1"


@pytest.mark.asyncio
async def test_head_convenience_sane_behavior() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(204, headers={"X-Resource": "present"})

    client = AsyncClient(
        base_url="https://api.example.test/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = await client.head(
        "/users/1",
        params={"include": "metadata"},
        headers={"X-Request-ID": "head-1"},
    )

    assert isinstance(response, ResponseData)
    assert response.status_code == 204
    assert response.headers["X-Resource"] == "present"
    assert requests[0].method == "HEAD"
    assert str(requests[0].url) == "https://api.example.test/api/v1/users/1?include=metadata"
    assert requests[0].headers["X-Request-ID"] == "head-1"


@pytest.mark.asyncio
async def test_convenience_method_non_2xx_response_returns_response_data_without_raising() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": "busy"})

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
        raise_for_status=False,
    )

    response = await client.get("/status")

    assert isinstance(response, ResponseData)
    assert response.status_code == 503
    assert response.json() == {"error": "busy"}


@pytest.mark.asyncio
async def test_convenience_method_preserves_base_path_joining_through_request() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = AsyncClient(
        base_url="https://api.example.test/api/v1",
        transport=httpx.MockTransport(handler),
    )

    await client.get("/users")

    assert str(requests[0].url) == "https://api.example.test/api/v1/users"


@pytest.mark.asyncio
async def test_convenience_method_omitted_timeout_uses_client_default_timeout() -> None:
    captured_timeouts: list[Any] = []
    client = AsyncClient(base_url="https://api.example.test", timeout=7.5)

    async def request_spy(**kwargs: Any) -> httpx.Response:
        captured_timeouts.append(kwargs["timeout"])
        return httpx.Response(200)

    client._client.request = request_spy  # type: ignore[method-assign]

    await client.get("/users")

    assert captured_timeouts == [7.5]


@pytest.mark.asyncio
async def test_convenience_method_explicit_timeout_none_overrides_client_default_timeout() -> None:
    captured_timeouts: list[Any] = []
    client = AsyncClient(base_url="https://api.example.test", timeout=7.5)

    async def request_spy(**kwargs: Any) -> httpx.Response:
        captured_timeouts.append(kwargs["timeout"])
        return httpx.Response(200)

    client._client.request = request_spy  # type: ignore[method-assign]

    await client.get("/users", timeout=None)

    assert captured_timeouts == [None]


@pytest.mark.asyncio
async def test_convenience_method_per_request_httpx_timeout_is_preserved_by_identity() -> None:
    captured_timeouts: list[Any] = []
    client = AsyncClient(base_url="https://api.example.test", timeout=7.5)
    timeout = httpx.Timeout(2.0)

    async def request_spy(**kwargs: Any) -> httpx.Response:
        captured_timeouts.append(kwargs["timeout"])
        return httpx.Response(200)

    client._client.request = request_spy  # type: ignore[method-assign]

    await client.get("/users", timeout=timeout)

    assert captured_timeouts == [timeout]
    assert captured_timeouts[0] is timeout


@pytest.mark.asyncio
async def test_convenience_method_idempotency_key_does_not_automatically_add_header() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    await client.post("/users", idempotency_key="request-123")

    assert "Idempotency-Key" not in requests[0].headers


@pytest.mark.asyncio
async def test_convenience_method_tags_do_not_create_request_behavior() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    response = await client.get("/users", tags=("users", "read"))

    assert response.status_code == 200
    assert str(requests[0].url) == "https://api.example.test/users"
    assert "tags" not in requests[0].headers


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
        raise_for_status=False,
    )

    response = await client.request("GET", "/missing")

    assert isinstance(response, ResponseData)
    assert response.status_code == 404
    assert response.json() == {"error": "nope"}


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [200, 302])
async def test_default_status_policy_returns_response_data_below_400(status_code: int) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code)

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    response = await client.get("/status")

    assert isinstance(response, ResponseData)
    assert response.status_code == status_code


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "expected_type"),
    [
        (400, HttpStatusError),
        (401, AuthenticationError),
        (403, AuthorizationError),
        (404, NotFoundError),
        (409, ConflictError),
        (422, ValidationError),
        (429, RateLimitError),
        (500, ServerError),
        (503, ServerError),
    ],
)
async def test_default_status_policy_raises_mapped_package_error(
    status_code: int,
    expected_type: type[HttpStatusError],
) -> None:
    raw_response = httpx.Response(status_code, json={"error": "failure"})

    async def handler(request: httpx.Request) -> httpx.Response:
        return raw_response

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(expected_type) as raised:
        await client.get("/status")

    error = raised.value
    assert type(error) is expected_type
    assert error.response.status_code == status_code
    assert error.response.raw is raw_response
    if status_code == 404:
        assert str(error) == "HTTP request failed with status 404"


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [404, 500])
async def test_disabled_status_policy_returns_error_response_data(status_code: int) -> None:
    raw_response = httpx.Response(status_code, json={"error": "failure"})

    async def handler(request: httpx.Request) -> httpx.Response:
        return raw_response

    client = AsyncClient(
        base_url="https://api.example.test",
        raise_for_status=False,
        transport=httpx.MockTransport(handler),
    )

    response = await client.get("/status")

    assert isinstance(response, ResponseData)
    assert response.status_code == status_code
    assert response.raw is raw_response
    assert response.json() == {"error": "failure"}


@pytest.mark.asyncio
async def test_mapped_status_error_uses_safe_diagnostic_context() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            headers={"Content-Type": "application/json", "Set-Cookie": "response-secret"},
            json={"error": "unauthorized", "echo": "Bearer test-async-secret"},
        )

    client = AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(AuthenticationError) as raised:
        await client.get(
            "/protected?token=test-query-secret&page=2",
            headers={"Authorization": "Bearer test-async-secret", "X-Request-ID": "safe-id"},
        )

    error = raised.value
    context = error.context
    assert context is not None
    assert context["method"] == "GET"
    assert context["url"] == "https://api.example.test/protected?token=<redacted>&page=2"
    assert context["request_headers"]["authorization"] == "<redacted>"
    assert context["request_headers"]["x-request-id"] == "safe-id"
    assert context["attempt"] == 1
    assert context["status_code"] == 401
    assert context["response_headers"]["set-cookie"] == "<redacted>"
    assert context["body_snippet"] == '{"error":"unauthorized","echo":"<redacted>"}'
    assert context["payload"] == {"error": "unauthorized", "echo": "<redacted>"}
    assert "test-async-secret" not in repr(context)
    assert "test-query-secret" not in repr(context)


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
async def test_async_client_aclose_exists() -> None:
    assert callable(AsyncClient.aclose)


@pytest.mark.asyncio
async def test_async_client_aclose_closes_internal_httpx_client() -> None:
    client = AsyncClient(base_url="https://api.example.test")

    result = await client.aclose()

    assert result is None
    assert client._client.is_closed


@pytest.mark.asyncio
async def test_async_client_explicit_aclose_works() -> None:
    client = AsyncClient(base_url="https://api.example.test")

    await client.aclose()

    assert client._client.is_closed


@pytest.mark.asyncio
async def test_async_client_double_aclose_does_not_crash() -> None:
    client = AsyncClient(base_url="https://api.example.test")

    await client.aclose()
    await client.aclose()

    assert client._client.is_closed


@pytest.mark.asyncio
async def test_async_client_aenter_returns_self() -> None:
    client = AsyncClient(base_url="https://api.example.test")

    assert await client.__aenter__() is client

    await client.aclose()


@pytest.mark.asyncio
async def test_async_client_context_manager_returns_self_and_closes_after_block() -> None:
    async with AsyncClient(base_url="https://api.example.test") as client:
        assert isinstance(client, AsyncClient)
        assert not client._client.is_closed

    assert client._client.is_closed


@pytest.mark.asyncio
async def test_async_client_context_manager_closes_when_block_raises() -> None:
    client: AsyncClient | None = None

    async def capture_and_raise() -> None:
        nonlocal client
        async with AsyncClient(base_url="https://api.example.test") as active_client:
            client = active_client
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        await capture_and_raise()

    assert client is not None
    assert client._client.is_closed


@pytest.mark.asyncio
async def test_async_client_context_manager_does_not_suppress_exceptions() -> None:
    with pytest.raises(RuntimeError, match="boom"):
        async with AsyncClient(base_url="https://api.example.test"):
            raise RuntimeError("boom")


@pytest.mark.asyncio
async def test_async_client_request_works_inside_context_manager() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    ) as client:
        response = await client.get("/status")

    assert isinstance(response, ResponseData)
    assert response.json() == {"ok": True}
    assert client._client.is_closed


@pytest.mark.asyncio
async def test_async_client_still_has_no_sync_context_manager_behavior() -> None:
    assert not hasattr(AsyncClient, "__enter__")
    assert not hasattr(AsyncClient, "__exit__")


@pytest.mark.asyncio
async def test_no_auth_retry_rate_limit_or_hooks_placeholder_parameters_exist() -> None:
    parameters = inspect.signature(AsyncClient.request).parameters

    assert "auth" not in parameters
    assert "retry_policy" not in parameters
    assert "rate_limiter" not in parameters
    assert "hooks" not in parameters


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method_name", "expected_method"),
    [
        ("get", "GET"),
        ("post", "POST"),
        ("put", "PUT"),
        ("patch", "PATCH"),
        ("delete", "DELETE"),
        ("head", "HEAD"),
    ],
)
async def test_convenience_methods_delegate_to_request(
    method_name: str,
    expected_method: str,
) -> None:
    calls: list[tuple[str, str, dict[str, Any]]] = []
    client = AsyncClient(base_url="https://api.example.test")

    async def request_spy(method: str, path: str, **kwargs: Any) -> ResponseData:
        calls.append((method, path, kwargs))
        return ResponseData(raw=httpx.Response(200))

    client.request = request_spy  # type: ignore[method-assign]

    response = await getattr(client, method_name)("/users", headers={"X-Test": "true"})

    assert isinstance(response, ResponseData)
    assert calls[0][0] == expected_method
    assert calls[0][1] == "/users"
    assert calls[0][2]["headers"] == {"X-Test": "true"}
