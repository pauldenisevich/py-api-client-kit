from __future__ import annotations

import pytest

# ------------------------------------------------
pytestmark = [pytest.mark.unit]


# ------------------------------------------------
def test_package_imports() -> None:
    import api_client_kit

    assert api_client_kit.__version__ == "0.0.0"
