from __future__ import annotations

from importlib.metadata import version

import pytest

pytestmark = [pytest.mark.unit]


def test_top_level_package_exports_sync_client() -> None:
    from api_client_kit import SyncClient

    assert SyncClient.__name__ == "SyncClient"


def test_top_level_package_exports_async_client() -> None:
    from api_client_kit import AsyncClient

    assert AsyncClient.__name__ == "AsyncClient"


def test_top_level_package_exports_request_options() -> None:
    from api_client_kit import RequestOptions

    assert RequestOptions.__name__ == "RequestOptions"


def test_top_level_package_exports_response_data() -> None:
    from api_client_kit import ResponseData

    assert ResponseData.__name__ == "ResponseData"


def test_top_level_exports_are_client_subpackage_definitions() -> None:
    import api_client_kit
    import api_client_kit.client

    assert api_client_kit.SyncClient is api_client_kit.client.SyncClient
    assert api_client_kit.AsyncClient is api_client_kit.client.AsyncClient
    assert api_client_kit.RequestOptions is api_client_kit.client.RequestOptions
    assert api_client_kit.ResponseData is api_client_kit.client.ResponseData


def test_top_level_all_contains_only_public_compatibility_surface() -> None:
    import api_client_kit

    assert api_client_kit.__all__ == (
        "AsyncClient",
        "RequestOptions",
        "ResponseData",
        "SyncClient",
        "__version__",
    )


def test_top_level_package_version_remains_stable() -> None:
    import api_client_kit

    assert api_client_kit.__version__ == "0.0.1"
    assert api_client_kit.__version__ == version("api-client-kit")


def test_client_subpackage_exports_sync_client() -> None:
    from api_client_kit.client import SyncClient

    assert SyncClient.__name__ == "SyncClient"


def test_client_subpackage_exports_async_client() -> None:
    from api_client_kit.client import AsyncClient

    assert AsyncClient.__name__ == "AsyncClient"


def test_client_subpackage_exports_request_options() -> None:
    from api_client_kit.client import RequestOptions

    assert RequestOptions.__name__ == "RequestOptions"


def test_client_subpackage_exports_response_data() -> None:
    from api_client_kit.client import ResponseData

    assert ResponseData.__name__ == "ResponseData"


def test_client_subpackage_exports_are_module_definitions() -> None:
    import api_client_kit.client as client
    import api_client_kit.client.async_client as async_client
    import api_client_kit.client.models as models
    import api_client_kit.client.sync_client as sync_client

    assert client.SyncClient is sync_client.SyncClient
    assert client.AsyncClient is async_client.AsyncClient
    assert client.RequestOptions is models.RequestOptions
    assert client.ResponseData is models.ResponseData


def test_client_subpackage_all_contains_only_public_client_api() -> None:
    import api_client_kit.client as client

    assert client.__all__ == (
        "AsyncClient",
        "RequestOptions",
        "ResponseData",
        "SyncClient",
    )


@pytest.mark.parametrize(
    "name",
    [
        "RequestContext",
        "join_url",
        "merge_headers",
        "resolve_timeout",
        "TimeoutValue",
    ],
)
def test_internal_names_are_not_exported_from_client_subpackage(name: str) -> None:
    import api_client_kit.client as client

    assert not hasattr(client, name)


@pytest.mark.parametrize(
    "name",
    [
        "RequestContext",
        "join_url",
        "merge_headers",
        "resolve_timeout",
        "TimeoutValue",
    ],
)
def test_internal_names_are_not_exported_from_top_level_package(name: str) -> None:
    import api_client_kit

    assert not hasattr(api_client_kit, name)
