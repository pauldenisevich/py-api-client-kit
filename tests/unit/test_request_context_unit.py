from __future__ import annotations

from dataclasses import FrozenInstanceError

import httpx
import pytest
from api_client_kit.client.models import RequestContext

pytestmark = [pytest.mark.unit]


def test_request_context_imports_from_client_models() -> None:
    assert RequestContext.__name__ == "RequestContext"


def test_request_context_requires_method_and_url() -> None:
    context = RequestContext(method="GET", url="https://api.example.test/users")

    assert context.method == "GET"
    assert context.url == "https://api.example.test/users"


def test_request_context_missing_required_fields_raise_type_error() -> None:
    with pytest.raises(TypeError, match=r"missing .* required positional"):
        RequestContext()

    with pytest.raises(TypeError, match=r"missing .* required positional"):
        RequestContext(method="GET")


def test_request_context_normalizes_method_to_uppercase() -> None:
    context = RequestContext(method="post", url="https://api.example.test/users")

    assert context.method == "POST"


def test_request_context_default_attempt_is_one() -> None:
    context = RequestContext(method="GET", url="https://api.example.test/users")

    assert context.attempt == 1


def test_request_context_default_optional_fields() -> None:
    context = RequestContext(method="GET", url="https://api.example.test/users")

    assert context.headers is None
    assert context.params is None
    assert context.json is None
    assert context.data is None
    assert context.timeout is None
    assert context.idempotency_key is None
    assert context.tags == ()


def test_request_context_stores_headers_and_params() -> None:
    headers = {"X-Test": "true"}
    params = {"limit": 10}

    context = RequestContext(
        method="GET",
        url="https://api.example.test/users",
        headers=headers,
        params=params,
    )

    assert context.headers is headers
    assert context.params is params


def test_request_context_stores_json_body() -> None:
    body = {"name": "Ada"}

    context = RequestContext(method="POST", url="https://api.example.test/users", json=body)

    assert context.json is body


def test_request_context_stores_data_body() -> None:
    body = b"raw-body"

    context = RequestContext(method="POST", url="https://api.example.test/uploads", data=body)

    assert context.data is body


def test_request_context_stores_float_timeout() -> None:
    context = RequestContext(method="GET", url="https://api.example.test/users", timeout=3.5)

    assert context.timeout == 3.5


def test_request_context_stores_httpx_timeout() -> None:
    timeout = httpx.Timeout(5.0)

    context = RequestContext(method="GET", url="https://api.example.test/users", timeout=timeout)

    assert context.timeout is timeout


def test_request_context_stores_idempotency_key() -> None:
    context = RequestContext(
        method="POST",
        url="https://api.example.test/users",
        idempotency_key="request-123",
    )

    assert context.idempotency_key == "request-123"


def test_request_context_stores_tags() -> None:
    tags = ("users", "write")

    context = RequestContext(method="POST", url="https://api.example.test/users", tags=tags)

    assert context.tags is tags


def test_request_context_is_frozen() -> None:
    context = RequestContext(method="GET", url="https://api.example.test/users")

    with pytest.raises(FrozenInstanceError):
        context.method = "POST"


def test_request_context_uses_slots_without_instance_dict() -> None:
    context = RequestContext(method="GET", url="https://api.example.test/users")

    assert not hasattr(context, "__dict__")


def test_request_context_is_not_in_models_all() -> None:
    import api_client_kit.client.models as models

    assert "RequestContext" not in models.__all__
    assert models.__all__ == ("RequestOptions", "ResponseData")


def test_request_context_is_not_exported_from_client_package() -> None:
    import api_client_kit.client as client

    assert not hasattr(client, "RequestContext")


def test_request_context_is_not_exported_from_top_level_package() -> None:
    import api_client_kit

    assert not hasattr(api_client_kit, "RequestContext")
