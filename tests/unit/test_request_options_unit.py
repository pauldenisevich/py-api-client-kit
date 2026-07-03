from __future__ import annotations

from dataclasses import FrozenInstanceError

import httpx
import pytest
from api_client_kit.client.models import RequestOptions

pytestmark = [pytest.mark.unit]


def test_request_options_imports_from_client_models() -> None:
    assert RequestOptions.__name__ == "RequestOptions"


def test_request_options_requires_method_and_path() -> None:
    options = RequestOptions(method="GET", path="/users")

    assert options.method == "GET"
    assert options.path == "/users"


def test_request_options_missing_required_fields_raise_type_error() -> None:
    with pytest.raises(TypeError, match=r"missing .* required positional"):
        RequestOptions()

    with pytest.raises(TypeError, match=r"missing .* required positional"):
        RequestOptions(method="GET")


def test_request_options_defaults() -> None:
    options = RequestOptions(method="GET", path="/users")

    assert options.params is None
    assert options.headers is None
    assert options.json is None
    assert options.data is None
    assert options.timeout is None
    assert options.idempotency_key is None
    assert options.tags == ()


def test_request_options_stores_params_and_headers() -> None:
    params = {"limit": 10}
    headers = {"X-Test": "true"}

    options = RequestOptions(method="GET", path="/users", params=params, headers=headers)

    assert options.params is params
    assert options.headers is headers


def test_request_options_stores_json_body() -> None:
    body = {"name": "Ada"}

    options = RequestOptions(method="POST", path="/users", json=body)

    assert options.json is body


def test_request_options_stores_data_body() -> None:
    body = b"raw-body"

    options = RequestOptions(method="POST", path="/uploads", data=body)

    assert options.data is body


def test_request_options_stores_float_timeout() -> None:
    options = RequestOptions(method="GET", path="/users", timeout=3.5)

    assert options.timeout == 3.5


def test_request_options_stores_httpx_timeout() -> None:
    timeout = httpx.Timeout(5.0)

    options = RequestOptions(method="GET", path="/users", timeout=timeout)

    assert options.timeout is timeout


def test_request_options_stores_idempotency_key() -> None:
    options = RequestOptions(method="POST", path="/users", idempotency_key="request-123")

    assert options.idempotency_key == "request-123"


def test_request_options_stores_tags() -> None:
    tags = ("users", "write")

    options = RequestOptions(method="POST", path="/users", tags=tags)

    assert options.tags is tags


def test_request_options_is_frozen() -> None:
    options = RequestOptions(method="GET", path="/users")

    with pytest.raises(FrozenInstanceError):
        options.method = "POST"


def test_request_options_uses_slots_without_instance_dict() -> None:
    options = RequestOptions(method="GET", path="/users")

    assert not hasattr(options, "__dict__")


def test_request_options_is_in_models_all() -> None:
    import api_client_kit.client.models as models

    assert "RequestOptions" in models.__all__
    assert models.__all__ == ("RequestOptions", "ResponseData")
