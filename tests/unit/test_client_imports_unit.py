from __future__ import annotations

import importlib
from importlib.metadata import version
from types import ModuleType

import pytest

# ------------------------------------------------
pytestmark = [pytest.mark.unit]

CLIENT_MODULES = (
    "api_client_kit.client",
    "api_client_kit.client.models",
    "api_client_kit.client.sync_client",
    "api_client_kit.client.async_client",
    "api_client_kit.client.urls",
    "api_client_kit.client.headers",
)


# ------------------------------------------------
@pytest.mark.parametrize("module_name", CLIENT_MODULES)
def test_client_modules_import(module_name: str) -> None:
    module = importlib.import_module(module_name)

    assert isinstance(module, ModuleType)
    assert module.__name__ == module_name


# ------------------------------------------------
def test_top_level_package_import_and_version_remain_stable() -> None:
    import api_client_kit

    assert api_client_kit.__version__ == "0.0.1"
    assert api_client_kit.__version__ == version("api-client-kit")
