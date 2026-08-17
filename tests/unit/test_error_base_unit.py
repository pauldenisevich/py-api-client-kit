from __future__ import annotations

from collections.abc import Mapping

import pytest
from api_client_kit.errors import ApiClientError

pytestmark = [pytest.mark.unit]


def test_api_client_error_inherits_exception() -> None:
    error = ApiClientError("Request failed")

    assert issubclass(ApiClientError, Exception)
    assert isinstance(error, Exception)


def test_api_client_error_preserves_normal_exception_behavior() -> None:
    error = ApiClientError("Request failed")

    assert error.args == ("Request failed",)
    assert error.context is None
    assert str(error) == "Request failed"


def test_api_client_error_accepts_empty_message() -> None:
    error = ApiClientError("")

    assert error.args == ("",)
    assert str(error) == ""


def test_api_client_error_rejects_non_string_message() -> None:
    with pytest.raises(TypeError, match="message must be str"):
        ApiClientError(42)  # type: ignore[arg-type]


def test_api_client_error_stores_context() -> None:
    error = ApiClientError("Request failed", context={"status_code": 404})

    assert error.context == {"status_code": 404}


def test_api_client_error_preserves_explicit_empty_context() -> None:
    assert ApiClientError("Request failed", context={}).context == {}
    assert ApiClientError("Request failed").context is None


def test_api_client_error_rejects_non_mapping_context() -> None:
    with pytest.raises(TypeError, match="context must be a mapping or None"):
        ApiClientError("Request failed", context=[("status_code", 404)])  # type: ignore[arg-type]


def test_api_client_error_accepts_mapping_input() -> None:
    source: Mapping[str, object] = {"status_code": 404}

    assert ApiClientError("Request failed", context=source).context == {"status_code": 404}


def test_api_client_error_defensively_copies_source_context() -> None:
    source = {"status_code": 404}
    error = ApiClientError("Request failed", context=source)
    source["status_code"] = 500

    assert error.context == {"status_code": 404}


def test_api_client_error_defensively_copies_returned_context() -> None:
    error = ApiClientError("Request failed", context={"status_code": 404})
    returned = error.context

    assert isinstance(returned, dict)
    returned["status_code"] = 500

    assert error.context == {"status_code": 404}


def test_api_client_error_context_copy_is_shallow() -> None:
    nested = {"retry": 1}
    error = ApiClientError("Request failed", context={"metadata": nested})
    context = error.context

    assert isinstance(context, dict)
    assert context["metadata"] is nested


def test_api_client_error_str_renders_only_message_with_context() -> None:
    error = ApiClientError(
        "Request failed",
        context={"status_code": 500, "url": "https://api.example.test/items"},
    )

    assert str(error) == "Request failed"


def test_api_client_error_repr_renders_only_class_and_message() -> None:
    error = ApiClientError("Request failed", context={"status_code": 500})

    assert repr(error) == "ApiClientError('Request failed')"
    assert "status_code" not in repr(error)


def test_api_client_error_repr_uses_runtime_subclass_name() -> None:
    class CustomError(ApiClientError):
        pass

    assert repr(CustomError("failed")) == "CustomError('failed')"


def test_api_client_error_does_not_render_context_secret() -> None:
    error = ApiClientError(
        "Request failed",
        context={"authorization": "Bearer test-context-secret"},
    )

    assert "test-context-secret" not in str(error)
    assert "test-context-secret" not in repr(error)


def test_api_client_error_supports_native_exception_chaining() -> None:
    original = ValueError("original failure")

    with pytest.raises(ApiClientError) as exc_info:
        raise ApiClientError("safe high-level failure") from original

    error = exc_info.value
    assert error.args == ("safe high-level failure",)
    assert error.__cause__ is original
    assert isinstance(error.__cause__, ValueError)
    assert str(error.__cause__) == "original failure"
