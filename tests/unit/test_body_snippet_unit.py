from __future__ import annotations

import json

import pytest
from api_client_kit.redaction import safe_body_snippet

pytestmark = [pytest.mark.unit]

_TRUNCATION_MARKER = "…<truncated>"


def test_safe_body_snippet_marks_empty_text_and_bytes() -> None:
    assert safe_body_snippet("") == "<empty>"
    assert safe_body_snippet(b"") == "<empty>"


def test_safe_body_snippet_preserves_short_text_and_whitespace() -> None:
    body = "  request failed\nwith details  "

    assert safe_body_snippet(body) == body


def test_safe_body_snippet_preserves_exact_maximum_length() -> None:
    body = "a" * 1024

    assert safe_body_snippet(body) == body


def test_safe_body_snippet_truncates_over_maximum_length_deterministically() -> None:
    body = "a" * 1025

    result = safe_body_snippet(body)

    assert len(result) <= 1024
    assert result.endswith(_TRUNCATION_MARKER)
    assert result == safe_body_snippet(body)


def test_safe_body_snippet_bounds_substantially_long_text() -> None:
    result = safe_body_snippet("safe-text-" * 1_000)

    assert len(result) <= 1024
    assert result.endswith(_TRUNCATION_MARKER)


def test_safe_body_snippet_bounds_very_large_text_without_full_rendering() -> None:
    result = safe_body_snippet("safe-text-" * 1_000_000)

    assert len(result) <= 1024
    assert result.endswith(_TRUNCATION_MARKER)


def test_safe_body_snippet_scrubs_one_repeated_and_multiple_known_secrets() -> None:
    result = safe_body_snippet(
        "test-one then test-two then test-one",
        secret_values=("test-one", "test-two"),
    )

    assert result == "<redacted> then <redacted> then <redacted>"


def test_safe_body_snippet_ignores_empty_and_duplicate_secret_values() -> None:
    assert safe_body_snippet("test-secret", secret_values=("", "test-secret", "test-secret")) == (
        "<redacted>"
    )


def test_safe_body_snippet_does_not_rescan_generated_redaction_markers() -> None:
    assert safe_body_snippet("test-secret", secret_values=("test-secret", "red")) == "<redacted>"


def test_safe_body_snippet_prefers_longest_overlapping_source_secret() -> None:
    assert safe_body_snippet("test-secret", secret_values=("test-secret", "test")) == "<redacted>"


def test_safe_body_snippet_secret_order_does_not_change_source_matching() -> None:
    source = "test-secret and test"
    forward = safe_body_snippet(source, secret_values=("test-secret", "test"))
    reverse = safe_body_snippet(source, secret_values=("test", "test-secret"))

    assert forward == "<redacted> and <redacted>"
    assert reverse == forward


def test_safe_body_snippet_scrubs_before_truncation_boundary() -> None:
    known_value = "test-super-secret-token"
    result = safe_body_snippet(
        "a" * 1_015 + known_value + " trailing", secret_values=(known_value,)
    )

    assert known_value not in result
    assert "test-super-sec" not in result
    assert len(result) <= 1024
    assert result.endswith(_TRUNCATION_MARKER)


def test_safe_body_snippet_hides_an_oversized_secret_overlapping_the_boundary() -> None:
    known_value = "test-boundary-secret"
    result = safe_body_snippet(
        "a" * 1_000 + known_value + "z" * 1_000_000,
        secret_values=(known_value,),
    )

    assert known_value not in result
    assert "test-boundary" not in result
    assert len(result) <= 1024
    assert result.endswith(_TRUNCATION_MARKER)


def test_safe_body_snippet_hides_a_secret_prefix_at_the_oversized_boundary() -> None:
    known_value = "test-outside-secret"
    result = safe_body_snippet(
        "a" * 1_008 + known_value + "z" * 1_000_000,
        secret_values=(known_value,),
    )

    assert known_value not in result
    assert "test" not in result
    assert result == "a" * 1_008 + _TRUNCATION_MARKER


def test_safe_body_snippet_scrubs_a_complete_secret_at_the_oversized_boundary() -> None:
    known_value = "test-edge-secret"
    result = safe_body_snippet(
        "a" * (1_012 - len(known_value)) + known_value + "z" * 1_000_000,
        secret_values=(known_value,),
    )

    assert result == "a" * (1_012 - len(known_value)) + "<redacted>" + _TRUNCATION_MARKER


def test_safe_body_snippet_processes_utf8_bytes_as_text() -> None:
    assert safe_body_snippet("café".encode()) == "café"
    assert safe_body_snippet(b"test-secret", secret_values=("test-secret",)) == "<redacted>"


def test_safe_body_snippet_marks_invalid_utf8_bytes_as_binary() -> None:
    body = b"\xff\xfe\x00"

    result = safe_body_snippet(body)

    assert result == "<binary body: 3 bytes>"
    assert "\\xff" not in result


def test_safe_body_snippet_redacts_valid_json_object_nested_values_and_arrays() -> None:
    body = (
        '{"username":"alice","password":"test-password",'
        '"profile":{"api_key":"test-key"},"items":[{"token":"test-token"}]}'
    )

    result = safe_body_snippet(body)

    assert result == (
        '{"username":"alice","password":"<redacted>",'
        '"profile":{"api_key":"<redacted>"},"items":[{"token":"<redacted>"}]}'
    )


@pytest.mark.parametrize(
    ("body", "expected"),
    [('"hello"', '"hello"'), ("42", "42"), ("true", "true"), ("null", "null")],
)
def test_safe_body_snippet_renders_valid_json_scalars(body: str, expected: str) -> None:
    assert safe_body_snippet(body) == expected


def test_safe_body_snippet_scrubs_known_secrets_in_safe_json_fields_and_scalars() -> None:
    known_value = "test-token-secret"

    object_result = safe_body_snippet(
        '{"message":"Authentication failed for test-token-secret"}',
        secret_values=(known_value,),
    )
    scalar_result = safe_body_snippet('"test-token-secret"', secret_values=(known_value,))

    assert known_value not in object_result
    assert "<redacted>" in object_result
    assert scalar_result == '"<redacted>"'


def test_safe_body_snippet_uses_the_canonical_marker_for_json_safe_fields() -> None:
    result = safe_body_snippet(
        '{"message":"test-secret"}',
        secret_values=("test-secret", "red"),
    )

    assert json.loads(result) == {"message": "<redacted>"}


@pytest.mark.parametrize(
    "known_value",
    [
        'test-quote-"-secret',
        r"test-backslash-\-secret",
        "test-newline-\n-secret",
    ],
)
def test_safe_body_snippet_scrubs_escaped_known_json_values(known_value: str) -> None:
    body = json.dumps({"message": f"Authentication failed for {known_value}"})

    result = safe_body_snippet(body, secret_values=(known_value,))

    escaped_known_value = json.dumps(known_value)[1:-1]
    assert known_value not in result
    assert escaped_known_value not in result
    assert "<redacted>" in result
    assert json.loads(result) == {"message": "Authentication failed for <redacted>"}


def test_safe_body_snippet_falls_back_to_text_for_malformed_json() -> None:
    body = '{"password":"test-secret"'

    assert safe_body_snippet(body) == body
    assert safe_body_snippet(body, secret_values=("test-secret",)) == '{"password":"<redacted>"'


def test_safe_body_snippet_skips_structured_parsing_above_ceiling() -> None:
    known_value = "test-large-secret"
    body = '{"password":"test-large-secret","padding":"' + "a" * 65_536 + '"}'

    result = safe_body_snippet(body, secret_values=(known_value,))

    assert len(result) <= 1024
    assert result.endswith(_TRUNCATION_MARKER)
    assert known_value not in result
    assert '"password":"<redacted>"' in result


def test_safe_body_snippet_is_idempotent_for_the_canonical_marker() -> None:
    assert safe_body_snippet("token=<redacted>") == "token=<redacted>"
    assert (
        safe_body_snippet("test-secret", secret_values=("<redacted>", "test-secret"))
        == "<redacted>"
    )


@pytest.mark.parametrize("body", [None, {}, [], bytearray(b"body"), memoryview(b"body")])
def test_safe_body_snippet_rejects_unsupported_body_types(body: object) -> None:
    with pytest.raises(TypeError, match=r"body must be str or bytes"):
        safe_body_snippet(body)  # type: ignore[arg-type]


def test_safe_body_snippet_compact_json_is_parseable() -> None:
    result = safe_body_snippet('{"safe": [1, 2]}')

    assert result == '{"safe":[1,2]}'
    assert json.loads(result) == {"safe": [1, 2]}
