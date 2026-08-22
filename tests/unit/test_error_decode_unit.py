from __future__ import annotations

import json

import httpx
import pytest
from api_client_kit.client.models import ResponseData
from api_client_kit.errors import ApiClientError, DecodeError, HttpStatusError

pytestmark = [pytest.mark.unit]


def test_decode_error_has_the_expected_hierarchy() -> None:
    assert issubclass(DecodeError, ApiClientError)
    assert issubclass(DecodeError, Exception)
    assert not issubclass(DecodeError, HttpStatusError)
    assert not issubclass(DecodeError, ValueError)


def test_decode_error_preserves_response_and_base_behavior() -> None:
    raw_response = httpx.Response(200)
    response = ResponseData(raw=raw_response)

    error = DecodeError("Response decoding failed", response=response)

    assert error.args == ("Response decoding failed",)
    assert error.response is response
    assert error.response.raw is raw_response
    assert error.context is None
    assert str(error) == "Response decoding failed"
    assert repr(error) == "DecodeError('Response decoding failed')"
    assert not hasattr(error, "raw")
    assert not hasattr(error, "raw_response")
    assert not hasattr(error, "httpx_response")


def test_decode_error_requires_message_and_keyword_only_response() -> None:
    response = ResponseData(raw=httpx.Response(200))

    with pytest.raises(TypeError):
        DecodeError("Response decoding failed")  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        DecodeError(response=response)  # type: ignore[call-arg]


def test_decode_error_inherits_context_support() -> None:
    response = ResponseData(raw=httpx.Response(200))
    context = {
        "status_code": 200,
        "content_type": "application/json",
        "body_snippet": "{invalid",
    }

    error = DecodeError("Response decoding failed", response=response, context=context)

    assert error.context == context


def test_decode_error_does_not_render_response_or_context_secrets() -> None:
    raw_response = httpx.Response(
        200,
        headers={"X-Test-Secret": "test-decode-response-secret"},
        content=b"test-decode-response-secret",
    )
    response = ResponseData(raw=raw_response)
    error = DecodeError(
        "Response decoding failed",
        response=response,
        context={"secret": "test-decode-context-secret"},
    )

    assert "test-decode-response-secret" not in str(error)
    assert "test-decode-response-secret" not in repr(error)
    assert "test-decode-context-secret" not in str(error)
    assert "test-decode-context-secret" not in repr(error)


def test_decode_error_supports_native_json_decode_error_chaining() -> None:
    response = ResponseData(raw=httpx.Response(200))

    with pytest.raises(json.JSONDecodeError) as cause_info:
        json.loads("{")

    original = cause_info.value
    with pytest.raises(DecodeError) as exc_info:
        raise DecodeError("Response decoding failed", response=response) from original

    error = exc_info.value
    assert error.__cause__ is original
    assert isinstance(error.__cause__, json.JSONDecodeError)
    assert error.response is response
    assert error.args == ("Response decoding failed",)
    assert str(error) == "Response decoding failed"
    assert repr(error) == "DecodeError('Response decoding failed')"
