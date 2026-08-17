from __future__ import annotations

import api_client_kit
import api_client_kit.errors as errors
import pytest
from api_client_kit.errors import ApiClientError, NetworkError, TimeoutError  # noqa: A004

pytestmark = [pytest.mark.unit]


def test_errors_subpackage_exports_package_error_types() -> None:
    assert errors.__all__ == ("ApiClientError", "NetworkError", "TimeoutError")
    assert errors.ApiClientError is ApiClientError
    assert errors.NetworkError is NetworkError
    assert errors.TimeoutError is TimeoutError


def test_top_level_package_does_not_export_error_types() -> None:
    assert not hasattr(api_client_kit, "ApiClientError")
    assert not hasattr(api_client_kit, "NetworkError")
    assert not hasattr(api_client_kit, "TimeoutError")
