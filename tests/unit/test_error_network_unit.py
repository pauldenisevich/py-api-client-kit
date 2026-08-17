from __future__ import annotations

import builtins

import pytest
from api_client_kit.errors import ApiClientError, NetworkError, TimeoutError  # noqa: A004

pytestmark = [pytest.mark.unit]


def test_network_and_timeout_errors_have_the_expected_hierarchy() -> None:
    assert issubclass(NetworkError, ApiClientError)
    assert issubclass(TimeoutError, NetworkError)
    assert issubclass(TimeoutError, ApiClientError)
    assert issubclass(NetworkError, Exception)
    assert issubclass(TimeoutError, Exception)


def test_package_timeout_error_is_distinct_from_builtin_timeout_error() -> None:
    assert not issubclass(TimeoutError, builtins.TimeoutError)


def test_network_error_inherits_base_construction_and_context_behavior() -> None:
    error = NetworkError(
        "Network request failed",
        context={"method": "GET", "attempt": 1},
    )

    assert error.args == ("Network request failed",)
    assert error.context == {"method": "GET", "attempt": 1}
    assert str(error) == "Network request failed"
    assert repr(error) == "NetworkError('Network request failed')"


def test_timeout_error_inherits_base_construction_behavior() -> None:
    error = TimeoutError("Request timed out")

    assert error.args == ("Request timed out",)
    assert error.context is None
    assert str(error) == "Request timed out"
    assert repr(error) == "TimeoutError('Request timed out')"


def test_network_error_does_not_render_context_secrets() -> None:
    error = NetworkError(
        "Network request failed",
        context={"authorization": "Bearer test-transport-secret"},
    )

    assert "test-transport-secret" not in str(error)
    assert "test-transport-secret" not in repr(error)


@pytest.mark.parametrize("error_type", [NetworkError, TimeoutError])
def test_network_errors_require_an_explicit_message(
    error_type: type[NetworkError],
) -> None:
    with pytest.raises(TypeError):
        error_type()  # type: ignore[call-arg]


def test_network_error_supports_native_exception_chaining() -> None:
    original = OSError("connection reset")

    with pytest.raises(NetworkError) as exc_info:
        raise NetworkError("Network request failed") from original

    error = exc_info.value
    assert error.__cause__ is original
    assert isinstance(error.__cause__, OSError)
    assert isinstance(error, ApiClientError)


def test_timeout_error_can_chain_from_builtin_timeout_error() -> None:
    original = builtins.TimeoutError("socket timeout")

    with pytest.raises(TimeoutError) as exc_info:
        raise TimeoutError("Request timed out") from original

    error = exc_info.value
    assert not isinstance(error, builtins.TimeoutError)
    assert error.__cause__ is original
    assert isinstance(error.__cause__, builtins.TimeoutError)
