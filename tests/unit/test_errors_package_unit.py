from __future__ import annotations

import api_client_kit
import api_client_kit.errors as errors
import pytest
from api_client_kit.errors import ApiClientError

pytestmark = [pytest.mark.unit]


def test_errors_subpackage_exports_api_client_error() -> None:
    assert errors.__all__ == ("ApiClientError",)
    assert errors.ApiClientError is ApiClientError


def test_top_level_package_does_not_export_api_client_error() -> None:
    assert not hasattr(api_client_kit, "ApiClientError")
