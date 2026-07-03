from __future__ import annotations

import httpx
import pytest
from api_client_kit.client.timeouts import resolve_timeout

pytestmark = [pytest.mark.unit]


def test_resolve_timeout_imports_from_client_timeouts() -> None:
    assert resolve_timeout.__name__ == "resolve_timeout"


def test_resolve_timeout_is_in_timeouts_all() -> None:
    import api_client_kit.client.timeouts as timeouts

    assert "resolve_timeout" in timeouts.__all__
    assert timeouts.__all__ == ("resolve_timeout",)


def test_timeout_value_is_not_in_timeouts_all() -> None:
    import api_client_kit.client.timeouts as timeouts

    assert "TimeoutValue" not in timeouts.__all__


def test_resolve_timeout_returns_default_float_when_request_timeout_omitted() -> None:
    assert resolve_timeout(default_timeout=5.0) == 5.0


def test_resolve_timeout_returns_default_httpx_timeout_when_request_timeout_omitted() -> None:
    default_timeout = httpx.Timeout(5.0)

    assert resolve_timeout(default_timeout=default_timeout) is default_timeout


def test_resolve_timeout_returns_default_none_when_request_timeout_omitted() -> None:
    assert resolve_timeout(default_timeout=None) is None


def test_resolve_timeout_request_float_overrides_default_float() -> None:
    assert resolve_timeout(default_timeout=5.0, request_timeout=1.0) == 1.0


def test_resolve_timeout_request_httpx_timeout_overrides_default_float() -> None:
    request_timeout = httpx.Timeout(2.0)

    assert resolve_timeout(default_timeout=5.0, request_timeout=request_timeout) is request_timeout


def test_resolve_timeout_request_none_overrides_default_float() -> None:
    assert resolve_timeout(default_timeout=5.0, request_timeout=None) is None


def test_resolve_timeout_preserves_selected_httpx_timeout_by_identity() -> None:
    default_timeout = httpx.Timeout(5.0)
    request_timeout = httpx.Timeout(2.0)

    assert resolve_timeout(default_timeout=default_timeout) is default_timeout
    assert (
        resolve_timeout(default_timeout=default_timeout, request_timeout=request_timeout)
        is request_timeout
    )


def test_resolve_timeout_returns_selected_value_without_copying_or_conversion() -> None:
    default_timeout = httpx.Timeout(connect=1.0, read=2.0, write=3.0, pool=4.0)
    request_timeout = httpx.Timeout(connect=5.0, read=6.0, write=7.0, pool=8.0)

    selected_default = resolve_timeout(default_timeout=default_timeout)
    selected_request = resolve_timeout(
        default_timeout=default_timeout,
        request_timeout=request_timeout,
    )

    assert selected_default is default_timeout
    assert selected_request is request_timeout


def test_resolve_timeout_is_not_exported_from_client_package() -> None:
    import api_client_kit.client as client

    assert not hasattr(client, "resolve_timeout")


def test_resolve_timeout_is_not_exported_from_top_level_package() -> None:
    import api_client_kit

    assert not hasattr(api_client_kit, "resolve_timeout")
