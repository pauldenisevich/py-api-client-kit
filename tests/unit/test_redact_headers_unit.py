from __future__ import annotations

import httpx
import pytest
from api_client_kit.redaction import redact_headers

pytestmark = [pytest.mark.unit]


@pytest.mark.parametrize(
    "name",
    [
        "Authorization",
        "Proxy-Authorization",
        "Cookie",
        "Set-Cookie",
        "X-API-Key",
        "API-Key",
        "X-Auth-Token",
        "X-Access-Token",
    ],
)
def test_redact_headers_redacts_each_sensitive_header(name: str) -> None:
    redacted = redact_headers({name: "test-secret"})

    assert redacted[name] == "<redacted>"


@pytest.mark.parametrize(
    "name",
    ["authorization", "AUTHORIZATION", "proxy-authorization", "x-api-key", "X-Access-Token"],
)
def test_redact_headers_matches_sensitive_names_case_insensitively(name: str) -> None:
    redacted = redact_headers({name: "test-secret"})

    assert redacted[name] == "<redacted>"


def test_redact_headers_preserves_safe_headers_in_a_mixed_mapping() -> None:
    redacted = redact_headers(
        {
            "Authorization": "test-authorization-secret",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "api-client-kit",
            "X-Request-ID": "request-123",
            "X-Custom-Header": "custom-value",
        }
    )

    assert redacted["Authorization"] == "<redacted>"
    assert redacted["Accept"] == "application/json"
    assert redacted["Content-Type"] == "application/json"
    assert redacted["User-Agent"] == "api-client-kit"
    assert redacted["X-Request-ID"] == "request-123"
    assert redacted["X-Custom-Header"] == "custom-value"


def test_redact_headers_accepts_mapping_without_mutating_it() -> None:
    original = {
        "Authorization": "test-authorization-secret",
        "Accept": "application/json",
    }

    redacted = redact_headers(original)

    assert isinstance(redacted, httpx.Headers)
    assert original == {
        "Authorization": "test-authorization-secret",
        "Accept": "application/json",
    }


def test_redact_headers_accepts_httpx_headers_without_mutating_them() -> None:
    original = httpx.Headers(
        {"Authorization": "test-authorization-secret", "Accept": "application/json"}
    )

    redacted = redact_headers(original)

    assert isinstance(redacted, httpx.Headers)
    assert redacted is not original
    assert original["Authorization"] == "test-authorization-secret"
    assert original["Accept"] == "application/json"


@pytest.mark.parametrize("headers", [{}, httpx.Headers()])
def test_redact_headers_returns_empty_headers_for_empty_input(
    headers: dict[str, str] | httpx.Headers,
) -> None:
    redacted = redact_headers(headers)

    assert isinstance(redacted, httpx.Headers)
    assert redacted == httpx.Headers()
    assert redacted is not headers


@pytest.mark.parametrize(
    "name",
    ["X-Authorization-Mode", "Authorization-Policy", "X-Cookie-Behavior"],
)
def test_redact_headers_uses_exact_sensitive_names(name: str) -> None:
    redacted = redact_headers({name: "Bearer test-token"})

    assert redacted[name] == "Bearer test-token"


def test_redact_headers_preserves_repeated_safe_header_values() -> None:
    redacted = redact_headers(
        httpx.Headers([("X-Custom-Header", "first"), ("X-Custom-Header", "second")])
    )

    assert redacted.multi_items() == [
        ("x-custom-header", "first"),
        ("x-custom-header", "second"),
    ]


def test_redact_headers_redacts_every_repeated_sensitive_value() -> None:
    original = httpx.Headers(
        [
            ("Set-Cookie", "test-set-cookie-secret-one"),
            ("Set-Cookie", "test-set-cookie-secret-two"),
            ("Authorization", "test-authorization-secret"),
        ]
    )

    redacted = redact_headers(original)

    assert redacted.multi_items() == [
        ("set-cookie", "<redacted>"),
        ("set-cookie", "<redacted>"),
        ("authorization", "<redacted>"),
    ]
    assert original.multi_items() == [
        ("set-cookie", "test-set-cookie-secret-one"),
        ("set-cookie", "test-set-cookie-secret-two"),
        ("authorization", "test-authorization-secret"),
    ]


def test_redact_headers_keeps_fake_secrets_out_of_values_and_representations() -> None:
    fake_secrets = (
        "test-authorization-secret",
        "test-proxy-auth-secret",
        "test-cookie-secret",
        "test-set-cookie-secret",
        "test-api-key-secret",
        "test-auth-token-secret",
        "test-access-token-secret",
    )
    redacted = redact_headers(
        {
            "Authorization": fake_secrets[0],
            "Proxy-Authorization": fake_secrets[1],
            "Cookie": fake_secrets[2],
            "Set-Cookie": fake_secrets[3],
            "X-API-Key": fake_secrets[4],
            "X-Auth-Token": fake_secrets[5],
            "X-Access-Token": fake_secrets[6],
        }
    )

    rendered = f"{redacted!s}\n{redacted!r}\n{redacted.multi_items()!r}"

    assert all(value == "<redacted>" for _, value in redacted.multi_items())
    for secret in fake_secrets:
        assert secret not in rendered


def test_redact_headers_is_exposed_only_from_redaction_subpackage() -> None:
    import api_client_kit
    import api_client_kit.redaction as redaction

    assert redaction.__all__ == (
        "redact_headers",
        "redact_payload",
        "redact_url",
        "safe_body_snippet",
    )
    assert redaction.redact_headers is redact_headers
    assert not hasattr(api_client_kit, "redact_headers")
