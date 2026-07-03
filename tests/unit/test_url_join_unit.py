from __future__ import annotations

import pytest
from api_client_kit.client.urls import join_url

pytestmark = [pytest.mark.unit]


def test_join_url_imports_from_client_urls() -> None:
    assert join_url.__name__ == "join_url"


def test_join_url_is_in_urls_all() -> None:
    import api_client_kit.client.urls as urls

    assert "join_url" in urls.__all__
    assert urls.__all__ == ("join_url",)


@pytest.mark.parametrize(
    ("base_url", "path", "expected"),
    [
        ("https://api.example.com", "users", "https://api.example.com/users"),
        ("https://api.example.com/", "users", "https://api.example.com/users"),
        ("https://api.example.com", "/users", "https://api.example.com/users"),
        ("https://api.example.com/", "/users", "https://api.example.com/users"),
    ],
)
def test_join_url_handles_all_base_and_path_slash_combinations(
    base_url: str,
    path: str,
    expected: str,
) -> None:
    assert join_url(base_url, path) == expected


def test_join_url_preserves_base_api_prefix_with_leading_path_slash() -> None:
    assert join_url("https://api.example.com/v1", "/users") == "https://api.example.com/v1/users"


def test_join_url_preserves_base_api_prefix_with_trailing_base_slash() -> None:
    assert join_url("https://api.example.com/v1/", "users") == "https://api.example.com/v1/users"


def test_join_url_preserves_deeper_base_api_prefix() -> None:
    assert (
        join_url("https://api.example.com/api/v1/", "/users")
        == "https://api.example.com/api/v1/users"
    )


def test_join_url_preserves_request_path_query_string() -> None:
    assert (
        join_url("https://api.example.com/v1", "/users?limit=10&active=true")
        == "https://api.example.com/v1/users?limit=10&active=true"
    )


@pytest.mark.parametrize(
    ("base_url", "expected"),
    [
        ("https://api.example.com", "https://api.example.com"),
        ("https://api.example.com/", "https://api.example.com"),
        ("https://api.example.com/v1", "https://api.example.com/v1"),
        ("https://api.example.com/v1/", "https://api.example.com/v1"),
    ],
)
def test_join_url_empty_path_returns_base_without_trailing_slash(
    base_url: str,
    expected: str,
) -> None:
    assert join_url(base_url) == expected
    assert join_url(base_url, "") == expected


def test_join_url_root_slash_path_returns_base_without_trailing_slash() -> None:
    assert join_url("https://api.example.com/v1", "/") == "https://api.example.com/v1"


def test_join_url_does_not_add_accidental_double_slashes_between_paths() -> None:
    result = join_url("https://api.example.com/api/v1///", "///users///")

    assert result == "https://api.example.com/api/v1/users"


@pytest.mark.parametrize(
    ("base_url", "path"),
    [
        ("", "/users"),
        ("/v1", "/users"),
        ("api.example.com/v1", "/users"),
        ("https:///v1", "/users"),
        ("ftp://api.example.com/v1", "/users"),
        ("https://api.example.com/v1?token=abc", "/users"),
        ("https://api.example.com/v1#frag", "/users"),
        ("https://api.example.com/v1", "https://evil.example/users"),
        ("https://api.example.com/v1", "//evil.example/users"),
        ("https://api.example.com/v1", "/users#section"),
    ],
)
def test_join_url_rejects_invalid_inputs(base_url: str, path: str) -> None:
    with pytest.raises(ValueError, match=r".+"):
        join_url(base_url, path)


def test_join_url_is_not_exported_from_client_package() -> None:
    import api_client_kit.client as client

    assert not hasattr(client, "join_url")


def test_join_url_is_not_exported_from_top_level_package() -> None:
    import api_client_kit

    assert not hasattr(api_client_kit, "join_url")
