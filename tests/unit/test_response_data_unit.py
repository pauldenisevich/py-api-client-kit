from __future__ import annotations

from dataclasses import FrozenInstanceError

import httpx
import pytest
from api_client_kit.client.models import ResponseData

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


def test_response_data_is_not_exported_from_client_package() -> None:
    import api_client_kit.client as client

    assert not hasattr(client, "ResponseData")


def test_response_data_is_not_exported_from_top_level_package() -> None:
    import api_client_kit

    assert not hasattr(api_client_kit, "ResponseData")
