from __future__ import annotations

from importlib.metadata import version

import pytest

pytestmark = [pytest.mark.unit]


def test_package_imports() -> None:
    import api_client_kit

    assert api_client_kit.__version__ == "0.0.1"


def test_package_version_matches_distribution_metadata() -> None:
    import api_client_kit

    assert api_client_kit.__version__ == version("api-client-kit")
