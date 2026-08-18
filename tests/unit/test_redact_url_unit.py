from __future__ import annotations

import httpx
import pytest
from api_client_kit.redaction import redact_url
from api_client_kit.redaction.urls import _sensitive_url_values

pytestmark = [pytest.mark.unit]


def test_redact_url_preserves_absolute_url_without_query() -> None:
    assert redact_url("https://api.example.test/v1/items") == "https://api.example.test/v1/items"


def test_redact_url_preserves_safe_query_text() -> None:
    assert (
        redact_url("https://api.example.test/items?search=hello%20world&page=2")
        == "https://api.example.test/items?search=hello%20world&page=2"
    )


def test_redact_url_redacts_mixed_query_and_relative_url() -> None:
    assert (
        redact_url("/items?page=2&token=test-token-secret&sort=name")
        == "/items?page=2&token=<redacted>&sort=name"
    )


@pytest.mark.parametrize(
    "name",
    [
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "key",
        "secret",
        "client_secret",
        "password",
        "session",
        "session_id",
        "auth",
        "authorization",
    ],
)
def test_redact_url_redacts_each_sensitive_query_name(name: str) -> None:
    secret = f"test-{name}-secret"
    redacted = redact_url(f"https://api.example.test/items?{name}={secret}")

    assert redacted == f"https://api.example.test/items?{name}=<redacted>"
    assert secret not in redacted


@pytest.mark.parametrize("name", ["TOKEN", "Access_Token", "API_KEY", "Authorization"])
def test_redact_url_matches_sensitive_query_names_case_insensitively(name: str) -> None:
    assert redact_url(f"/items?{name}=test-token-secret") == f"/items?{name}=<redacted>"


@pytest.mark.parametrize(
    "name",
    ["my_token", "token_type", "api_key_version", "authorization_mode", "secretary"],
)
def test_redact_url_uses_exact_sensitive_query_names(name: str) -> None:
    assert redact_url(f"/items?{name}=Bearer%20test-token") == f"/items?{name}=Bearer%20test-token"


def test_redact_url_preserves_repeated_parameters_and_ordering() -> None:
    redacted = redact_url("/items?tag=a&tag=b&token=one&token=two&page=3")

    assert redacted == "/items?tag=a&tag=b&token=<redacted>&token=<redacted>&page=3"
    assert "one" not in redacted
    assert "two" not in redacted


def test_redact_url_preserves_safe_encoding_and_removes_encoded_sensitive_value() -> None:
    redacted = redact_url("/items?search=hello%20world&token=test%2Fsecret%3Dabc")

    assert redacted == "/items?search=hello%20world&token=<redacted>"
    assert "test%2Fsecret%3Dabc" not in redacted
    assert "test/secret=abc" not in redacted


def test_redact_url_classifies_encoded_sensitive_query_names() -> None:
    redacted = redact_url("/items?api%5Fkey=test-api-key-secret&page=2")

    assert redacted == "/items?api%5Fkey=<redacted>&page=2"
    assert "test-api-key-secret" not in redacted


def test_redact_url_form_decodes_query_names_without_fuzzy_matching() -> None:
    assert (
        redact_url("/items?access+token=test-value&api%5Fkey=test-secret")
        == "/items?access+token=test-value&api%5Fkey=<redacted>"
    )


@pytest.mark.parametrize(
    ("url", "expected", "secrets"),
    [
        (
            "https://test-userinfo-user:test-userinfo-password@example.test:8443/items",
            "https://<redacted>:<redacted>@example.test:8443/items",
            ("test-userinfo-user", "test-userinfo-password"),
        ),
        (
            "https://test-userinfo-user@example.test/items",
            "https://<redacted>@example.test/items",
            ("test-userinfo-user",),
        ),
        (
            "https://test%2Duserinfo%2Duser:test%2Duserinfo%2Dpassword@example.test/items",
            "https://<redacted>:<redacted>@example.test/items",
            (
                "test%2Duserinfo%2Duser",
                "test%2Duserinfo%2Dpassword",
                "test-userinfo-user",
                "test-userinfo-password",
            ),
        ),
    ],
)
def test_redact_url_redacts_userinfo(url: str, expected: str, secrets: tuple[str, ...]) -> None:
    redacted = redact_url(url)

    assert redacted == expected
    assert all(secret not in redacted for secret in secrets)


def test_redact_url_redacts_userinfo_and_query_while_preserving_host_and_port() -> None:
    redacted = redact_url(
        "https://test-userinfo-user:test-userinfo-password@example.test:8443/items?token=test-token-secret"
    )

    assert redacted == "https://<redacted>:<redacted>@example.test:8443/items?token=<redacted>"
    assert "test-userinfo-user" not in redacted
    assert "test-userinfo-password" not in redacted
    assert "test-token-secret" not in redacted


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://example.test/path?x=1#section", "https://example.test/path?x=1"),
        (
            "https://example.test/path?x=1#access_token=test-fragment-secret",
            "https://example.test/path?x=1",
        ),
    ],
)
def test_redact_url_strips_fragments(url: str, expected: str) -> None:
    redacted = redact_url(url)

    assert redacted == expected
    assert "test-fragment-secret" not in redacted


def test_redact_url_preserves_empty_and_valueless_query_parameter_semantics() -> None:
    assert redact_url("/items?token=&token&page=") == "/items?token=<redacted>&token&page="


def test_sensitive_url_values_ignores_empty_sensitive_query_values() -> None:
    assert _sensitive_url_values("/items?token=&token&safe=visible") == ()


def test_sensitive_url_values_collects_userinfo_username_without_password() -> None:
    assert _sensitive_url_values("https://test-user@example.test/items") == ("test-user",)


def test_redact_url_accepts_httpx_url_without_mutating_it_and_returns_str() -> None:
    original = httpx.URL("https://api.example.test/items?token=test-token-secret&page=2")

    redacted = redact_url(original)

    assert isinstance(redacted, str)
    assert redacted == "https://api.example.test/items?token=<redacted>&page=2"
    assert str(original) == "https://api.example.test/items?token=test-token-secret&page=2"


def test_redact_url_is_not_exported_from_top_level_package() -> None:
    import api_client_kit

    assert not hasattr(api_client_kit, "redact_url")


def test_redact_url_rejects_unsupported_input_types() -> None:
    with pytest.raises(TypeError, match=r"url must be str or httpx.URL"):
        redact_url(42)  # type: ignore[arg-type]
