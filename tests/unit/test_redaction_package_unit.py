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
        "api_client_kit.redaction.urls",
    ],
)
def test_redaction_modules_import(module_name: str) -> None:
    module = importlib.import_module(module_name)

    assert isinstance(module, ModuleType)
    assert module.__name__ == module_name


def test_redaction_subpackage_exports_only_implemented_helpers() -> None:
    import api_client_kit.redaction as redaction
    from api_client_kit.redaction import redact_headers, redact_url

    assert redaction.__all__ == ("redact_headers", "redact_url")
    assert redaction.redact_headers is redact_headers
    assert redaction.redact_url is redact_url
