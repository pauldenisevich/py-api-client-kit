from __future__ import annotations

from types import MappingProxyType

import pytest
from api_client_kit.redaction import redact_payload

pytestmark = [pytest.mark.unit]


def test_redact_payload_preserves_safe_and_redacts_sensitive_flat_fields() -> None:
    redacted = redact_payload({"username": "alice", "password": "test-password-secret"})

    assert redacted == {"username": "alice", "password": "<redacted>"}


@pytest.mark.parametrize(
    "key",
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
        "auth",
        "authorization",
        "cookie",
        "session",
        "session_id",
    ],
)
def test_redact_payload_redacts_each_sensitive_key(key: str) -> None:
    assert redact_payload({key: f"test-{key}-secret"}) == {key: "<redacted>"}


@pytest.mark.parametrize("key", ["PASSWORD", "Api_Key", "AUTHORIZATION", "Cookie"])
def test_redact_payload_matches_sensitive_keys_case_insensitively(key: str) -> None:
    assert redact_payload({key: "test-secret"}) == {key: "<redacted>"}


@pytest.mark.parametrize(
    "key",
    [
        "my_token",
        "token_type",
        "api_key_version",
        "authentication_mode",
        "password_hint",
        "secretary",
    ],
)
def test_redact_payload_uses_exact_sensitive_key_matching(key: str) -> None:
    assert redact_payload({key: "safe-value"}) == {key: "safe-value"}


def test_redact_payload_does_not_url_decode_keys() -> None:
    assert redact_payload({"api%5Fkey": "safe-value"}) == {"api%5Fkey": "safe-value"}


def test_redact_payload_recurses_through_nested_mappings_and_lists() -> None:
    payload = {
        "profile": {
            "name": "Alice",
            "credentials": [
                {"api_key": "test-api-key-secret-one"},
                {"api_key": "test-api-key-secret-two"},
            ],
        }
    }

    assert redact_payload(payload) == {
        "profile": {
            "name": "Alice",
            "credentials": [{"api_key": "<redacted>"}, {"api_key": "<redacted>"}],
        }
    }


def test_redact_payload_recurses_through_tuples_at_every_supported_location() -> None:
    payload = (
        {"token": "test-top-level-token"},
        {"values": ("safe", {"password": "test-mapping-password"})},
        [("safe", {"cookie": "test-list-cookie"})],
    )

    assert redact_payload(payload) == (
        {"token": "<redacted>"},
        {"values": ("safe", {"password": "<redacted>"})},
        [("safe", {"cookie": "<redacted>"})],
    )


def test_redact_payload_preserves_mixed_structure_while_redacting_nested_values() -> None:
    payload = {"items": [({"token": "test-one"}, {"safe": {"password": "test-two"}})]}

    assert redact_payload(payload) == {
        "items": [({"token": "<redacted>"}, {"safe": {"password": "<redacted>"}})]
    }


def test_redact_payload_replaces_sensitive_container_branches_without_recursion() -> None:
    payload = {"auth": {"username": "alice", "token": "test-token-secret"}}

    assert redact_payload(payload) == {"auth": "<redacted>"}


class _OpaqueObject:
    pass


@pytest.mark.parametrize(
    "value",
    [None, 123, True, ["one", "two"], {"nested": "value"}, ("one", "two"), _OpaqueObject()],
)
def test_redact_payload_replaces_sensitive_values_of_every_type(value: object) -> None:
    assert redact_payload({"token": value}) == {"token": "<redacted>"}


def test_redact_payload_preserves_non_string_keys_and_recurses_into_their_values() -> None:
    assert redact_payload({1: {"password": "test-password-secret"}}) == {
        1: {"password": "<redacted>"}
    }


def test_redact_payload_normalizes_non_dict_mapping_without_mutating_it() -> None:
    original = MappingProxyType({"safe": {"token": "test-token-secret"}})

    redacted = redact_payload(original)

    assert isinstance(redacted, dict)
    assert type(redacted) is dict
    assert redacted == {"safe": {"token": "<redacted>"}}
    assert original == {"safe": {"token": "test-token-secret"}}


@pytest.mark.parametrize("value", [None, True, False, 123, 1.5, "safe", b"safe"])
def test_redact_payload_preserves_scalar_leaves(value: object) -> None:
    assert redact_payload(value) is value


def test_redact_payload_preserves_opaque_objects_and_unsupported_containers() -> None:
    opaque = _OpaqueObject()
    unsupported_set = {"test-token-secret"}
    unsupported_frozenset = frozenset({"test-password-secret"})

    redacted = redact_payload(
        {
            "value": opaque,
            "unsupported_set": unsupported_set,
            "unsupported_frozenset": unsupported_frozenset,
        }
    )

    assert redacted == {
        "value": opaque,
        "unsupported_set": unsupported_set,
        "unsupported_frozenset": unsupported_frozenset,
    }
    assert isinstance(redacted, dict)
    assert redacted["value"] is opaque
    assert redacted["unsupported_set"] is unsupported_set
    assert redacted["unsupported_frozenset"] is unsupported_frozenset


def test_redact_payload_rebuilds_supported_containers_without_mutating_input() -> None:
    original = {
        "password": "test-password-secret",
        "nested": [{"token": "test-token-secret"}, ("safe", {"api_key": "test-api-key-secret"})],
    }

    redacted = redact_payload(original)

    assert original == {
        "password": "test-password-secret",
        "nested": [
            {"token": "test-token-secret"},
            ("safe", {"api_key": "test-api-key-secret"}),
        ],
    }
    assert redacted == {
        "password": "<redacted>",
        "nested": [{"token": "<redacted>"}, ("safe", {"api_key": "<redacted>"})],
    }
    assert isinstance(redacted, dict)
    assert redacted is not original
    redacted_nested = redacted["nested"]
    original_nested = original["nested"]
    assert isinstance(redacted_nested, list)
    assert redacted_nested is not original_nested
    redacted_first = redacted_nested[0]
    original_first = original_nested[0]
    assert isinstance(redacted_first, dict)
    assert isinstance(original_first, dict)
    assert redacted_first is not original_first
    redacted_tuple = redacted_nested[1]
    original_tuple = original_nested[1]
    assert isinstance(redacted_tuple, tuple)
    assert isinstance(original_tuple, tuple)
    assert redacted_tuple is not original_tuple
    redacted_nested_mapping = redacted_tuple[1]
    original_nested_mapping = original_tuple[1]
    assert isinstance(redacted_nested_mapping, dict)
    assert isinstance(original_nested_mapping, dict)
    assert redacted_nested_mapping is not original_nested_mapping


def test_redact_payload_keeps_fake_secrets_out_of_its_representation() -> None:
    fake_secrets = (
        "test-token-secret",
        "test-password-secret",
        "test-api-key-secret",
        "test-auth-secret",
        "test-cookie-secret",
        "test-session-secret",
    )
    redacted = redact_payload(
        {
            "token": fake_secrets[0],
            "password": fake_secrets[1],
            "nested": {"api_key": fake_secrets[2], "auth": fake_secrets[3]},
            "cookie": fake_secrets[4],
            "session": fake_secrets[5],
        }
    )

    rendered = repr(redacted)

    assert isinstance(redacted, dict)
    assert all(value == "<redacted>" for key, value in redacted.items() if key != "nested")
    assert all(secret not in rendered for secret in fake_secrets)
