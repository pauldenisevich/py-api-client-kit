from __future__ import annotations

import pytest

pytestmark = [pytest.mark.unit]


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
        "SyncClient",
        "AsyncClient",
        "RequestOptions",
        "ResponseData",
    ],
)
def test_client_api_exports_are_deferred_from_top_level_package(name: str) -> None:
    import api_client_kit

    assert not hasattr(api_client_kit, name)
