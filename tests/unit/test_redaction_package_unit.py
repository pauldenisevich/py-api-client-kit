from __future__ import annotations

import importlib
from types import ModuleType

import pytest

pytestmark = [pytest.mark.unit]


@pytest.mark.parametrize(
    "module_name",
    [
        "api_client_kit.redaction",
        "api_client_kit.redaction.headers",
    ],
)
def test_redaction_modules_import(module_name: str) -> None:
    module = importlib.import_module(module_name)

    assert isinstance(module, ModuleType)
    assert module.__name__ == module_name
