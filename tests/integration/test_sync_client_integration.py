from __future__ import annotations

import inspect
import json as jsonlib
from typing import Any

import httpx
import pytest
from api_client_kit.client.models import ResponseData
from api_client_kit.client.sync_client import SyncClient

pytestmark = [pytest.mark.integration]


def test_sync_client_request_exists() -> None:
    assert callable(SyncClient.request)


def test_sync_client_convenience_methods_exist() -> None:
    convenience_methods: tuple[str, ...] = ("get", "post", "put", "patch", "delete", "head")

    assert all(callable(getattr(SyncClient, name)) for name in convenience_methods)


def test_convenience_method_body_parameter_surface_matches_scope() -> None:
    body_capable_methods: tuple[str, ...] = ("post", "put", "patch")
    body_free_methods: tuple[str, ...] = ("get", "delete", "head")

    for name in body_capable_methods:
        parameters = inspect.signature(getattr(SyncClient, name)).parameters
        assert "json" in parameters
        assert "data" in parameters

    for name in body_free_methods:
        parameters = inspect.signature(getattr(SyncClient, name)).parameters
        assert "json" not in parameters
        assert "data" not in parameters


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
def test_convenience_methods_send_expected_http_method(
    method_name: str,
    expected_method: str,
) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(204)

    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    response = getattr(client, method_name)("/resource")

    assert requests[0].method == expected_method
    assert isinstance(response, ResponseData)


def test_get_convenience_passes_params_and_headers() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    client.get(
        "/users",
        params={"limit": 10, "active": "true"},
        headers={"X-Request-ID": "abc"},
    )

    assert requests[0].url.params["limit"] == "10"
    assert requests[0].url.params["active"] == "true"
    assert requests[0].headers["X-Request-ID"] == "abc"


@pytest.mark.parametrize(
    ("method_name", "expected_method"),
    [
        ("post", "POST"),
        ("put", "PUT"),
        ("patch", "PATCH"),
    ],
)
def test_body_capable_convenience_methods_pass_json_payload(
    method_name: str,
    expected_method: str,
) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True})

    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    response = getattr(client, method_name)("/users", json={"name": "Ada"})

    assert requests[0].method == expected_method
    assert jsonlib.loads(requests[0].content) == {"name": "Ada"}
    assert response.json() == {"ok": True}


def test_delete_convenience_sane_behavior() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(202, json={"deleted": True})

    client = SyncClient(
        base_url="https://api.example.test/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.delete(
        "/users/1",
        params={"force": "true"},
        headers={"X-Request-ID": "delete-1"},
    )

    assert isinstance(response, ResponseData)
    assert response.status_code == 202
    assert requests[0].method == "DELETE"
    assert str(requests[0].url) == "https://api.example.test/api/v1/users/1?force=true"
    assert requests[0].headers["X-Request-ID"] == "delete-1"


def test_head_convenience_sane_behavior() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(204, headers={"X-Resource": "present"})

    client = SyncClient(
        base_url="https://api.example.test/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.head(
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


def test_convenience_method_non_2xx_response_returns_response_data_without_raising() -> None:
    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(lambda request: httpx.Response(503, json={"error": "busy"})),
    )

    response = client.get("/status")

    assert isinstance(response, ResponseData)
    assert response.status_code == 503
    assert response.json() == {"error": "busy"}


def test_convenience_method_preserves_base_path_joining_through_request() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = SyncClient(
        base_url="https://api.example.test/api/v1",
        transport=httpx.MockTransport(handler),
    )

    client.get("/users")

    assert str(requests[0].url) == "https://api.example.test/api/v1/users"


def test_convenience_method_omitted_timeout_uses_client_default_timeout() -> None:
    captured_timeouts: list[Any] = []
    client = SyncClient(base_url="https://api.example.test", timeout=7.5)

    def request_spy(**kwargs: Any) -> httpx.Response:
        captured_timeouts.append(kwargs["timeout"])
        return httpx.Response(200)

    client._client.request = request_spy  # type: ignore[method-assign]

    client.get("/users")

    assert captured_timeouts == [7.5]


def test_convenience_method_explicit_timeout_none_overrides_client_default_timeout() -> None:
    captured_timeouts: list[Any] = []
    client = SyncClient(base_url="https://api.example.test", timeout=7.5)

    def request_spy(**kwargs: Any) -> httpx.Response:
        captured_timeouts.append(kwargs["timeout"])
        return httpx.Response(200)

    client._client.request = request_spy  # type: ignore[method-assign]

    client.get("/users", timeout=None)

    assert captured_timeouts == [None]


def test_convenience_method_per_request_httpx_timeout_is_preserved_by_identity() -> None:
    captured_timeouts: list[Any] = []
    client = SyncClient(base_url="https://api.example.test", timeout=7.5)
    timeout = httpx.Timeout(2.0)

    def request_spy(**kwargs: Any) -> httpx.Response:
        captured_timeouts.append(kwargs["timeout"])
        return httpx.Response(200)

    client._client.request = request_spy  # type: ignore[method-assign]

    client.get("/users", timeout=timeout)

    assert captured_timeouts == [timeout]
    assert captured_timeouts[0] is timeout


def test_convenience_method_idempotency_key_does_not_automatically_add_header() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    client.post("/users", idempotency_key="request-123")

    assert "Idempotency-Key" not in requests[0].headers


def test_convenience_method_tags_do_not_create_request_behavior() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    response = client.get("/users", tags=("users", "read"))

    assert response.status_code == 200
    assert str(requests[0].url) == "https://api.example.test/users"
    assert "tags" not in requests[0].headers


def test_get_request_reaches_expected_url() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = SyncClient(
        base_url="https://api.example.test/v1",
        transport=httpx.MockTransport(handler),
    )

    client.request("GET", "users")

    assert str(requests[0].url) == "https://api.example.test/v1/users"


def test_base_url_prefix_is_preserved_when_path_starts_with_slash() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = SyncClient(
        base_url="https://api.example.test/api/v1",
        transport=httpx.MockTransport(handler),
    )

    client.request("GET", "/users")

    assert str(requests[0].url) == "https://api.example.test/api/v1/users"


def test_method_is_normalized_to_uppercase() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    client.request("post", "/users")

    assert requests[0].method == "POST"


def test_params_pass_through() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    client.request("GET", "/users", params={"limit": 10, "active": "true"})

    assert requests[0].url.params["limit"] == "10"
    assert requests[0].url.params["active"] == "true"


def test_headers_pass_through() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    client.request("GET", "/users", headers={"X-Request-ID": "abc"})

    assert requests[0].headers["X-Request-ID"] == "abc"


def test_default_headers_merge_with_request_headers() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = SyncClient(
        base_url="https://api.example.test",
        headers={"User-Agent": "api-client-kit"},
        transport=httpx.MockTransport(handler),
    )

    client.request("GET", "/users", headers={"X-Request-ID": "abc"})

    assert requests[0].headers["User-Agent"] == "api-client-kit"
    assert requests[0].headers["X-Request-ID"] == "abc"


def test_request_headers_override_default_headers() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = SyncClient(
        base_url="https://api.example.test",
        headers={"Authorization": "Bearer default-token"},
        transport=httpx.MockTransport(handler),
    )

    client.request("GET", "/users", headers={"authorization": "Bearer request-token"})

    assert requests[0].headers["Authorization"] == "Bearer request-token"


def test_response_is_wrapped_in_response_data_and_raw_response_access_works() -> None:
    raw_response = httpx.Response(202, text="accepted")

    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(lambda request: raw_response),
    )

    response = client.request("GET", "/jobs/1")

    assert isinstance(response, ResponseData)
    assert response.raw is raw_response
    assert response.status_code == 202
    assert response.text == "accepted"


def test_json_response_happy_path_works() -> None:
    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"ok": True})),
    )

    response = client.request("GET", "/status")

    assert response.json() == {"ok": True}


def test_non_2xx_response_returns_response_data_without_raising_status_error() -> None:
    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(lambda request: httpx.Response(404, json={"error": "nope"})),
    )

    response = client.request("GET", "/missing")

    assert isinstance(response, ResponseData)
    assert response.status_code == 404
    assert response.json() == {"error": "nope"}


def test_post_style_json_body_passes_through() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(201, json={"created": True})

    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    client.request("POST", "/users", json={"name": "Ada"})

    assert jsonlib.loads(requests[0].content) == {"name": "Ada"}


def test_data_body_passes_through() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(201)

    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    client.request("POST", "/uploads", data={"name": "Ada"})

    assert requests[0].content == b"name=Ada"


def test_client_default_timeout_is_used_when_request_timeout_is_omitted() -> None:
    captured_timeouts: list[Any] = []
    client = SyncClient(base_url="https://api.example.test", timeout=7.5)

    def request_spy(**kwargs: Any) -> httpx.Response:
        captured_timeouts.append(kwargs["timeout"])
        return httpx.Response(200)

    client._client.request = request_spy  # type: ignore[method-assign]

    client.request("GET", "/users")

    assert captured_timeouts == [7.5]


def test_per_request_float_timeout_overrides_client_default_timeout() -> None:
    captured_timeouts: list[Any] = []
    client = SyncClient(base_url="https://api.example.test", timeout=7.5)

    def request_spy(**kwargs: Any) -> httpx.Response:
        captured_timeouts.append(kwargs["timeout"])
        return httpx.Response(200)

    client._client.request = request_spy  # type: ignore[method-assign]

    client.request("GET", "/users", timeout=1.25)

    assert captured_timeouts == [1.25]


def test_explicit_timeout_none_overrides_client_default_timeout() -> None:
    captured_timeouts: list[Any] = []
    client = SyncClient(base_url="https://api.example.test", timeout=7.5)

    def request_spy(**kwargs: Any) -> httpx.Response:
        captured_timeouts.append(kwargs["timeout"])
        return httpx.Response(200)

    client._client.request = request_spy  # type: ignore[method-assign]

    client.request("GET", "/users", timeout=None)

    assert captured_timeouts == [None]


def test_idempotency_key_does_not_automatically_add_header() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    client.request("POST", "/users", idempotency_key="request-123")

    assert "Idempotency-Key" not in requests[0].headers


def test_tags_do_not_create_request_behavior() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    )

    response = client.request("GET", "/users", tags=("users", "read"))

    assert response.status_code == 200
    assert str(requests[0].url) == "https://api.example.test/users"
    assert "tags" not in requests[0].headers


def test_sync_client_still_has_no_close_method() -> None:
    assert not hasattr(SyncClient, "close")


def test_sync_client_still_has_no_context_manager_behavior() -> None:
    assert not hasattr(SyncClient, "__enter__")
    assert not hasattr(SyncClient, "__exit__")


def test_no_auth_retry_rate_limit_or_hooks_placeholder_parameters_exist() -> None:
    parameters = inspect.signature(SyncClient.request).parameters

    assert "auth" not in parameters
    assert "retry_policy" not in parameters
    assert "rate_limiter" not in parameters
    assert "hooks" not in parameters


def test_per_request_httpx_timeout_overrides_client_default_timeout() -> None:
    captured_timeouts: list[Any] = []
    client = SyncClient(base_url="https://api.example.test", timeout=7.5)
    timeout = httpx.Timeout(2.0)

    def request_spy(**kwargs: Any) -> httpx.Response:
        captured_timeouts.append(kwargs["timeout"])
        return httpx.Response(200)

    client._client.request = request_spy  # type: ignore[method-assign]

    client.request("GET", "/users", timeout=timeout)

    assert captured_timeouts == [timeout]
    assert captured_timeouts[0] is timeout


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
def test_convenience_methods_delegate_to_request(method_name: str, expected_method: str) -> None:
    calls: list[tuple[str, str, dict[str, Any]]] = []
    client = SyncClient(base_url="https://api.example.test")

    def request_spy(method: str, path: str, **kwargs: Any) -> ResponseData:
        calls.append((method, path, kwargs))
        return ResponseData(raw=httpx.Response(200))

    client.request = request_spy  # type: ignore[method-assign]

    getattr(client, method_name)("/users", headers={"X-Test": "true"})

    assert calls[0][0] == expected_method
    assert calls[0][1] == "/users"
    assert calls[0][2]["headers"] == {"X-Test": "true"}
