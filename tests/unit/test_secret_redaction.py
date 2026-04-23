"""Tests for src/lib/secret_redaction.py — T064."""

from __future__ import annotations

import pytest

from lib import secret_redaction


class TestRedactString:
    def test_plain_text_unchanged(self) -> None:
        text = "Agent completed scenario SCN-001 successfully."
        assert secret_redaction.redact(text) == text

    def test_openai_style_api_key_redacted(self) -> None:
        text = "key=sk-proj-abcdef1234567890abcdef1234567890abcdef12345678"
        assert "sk-proj-" not in secret_redaction.redact(text)
        assert "<REDACTED:" in secret_redaction.redact(text)

    def test_bearer_token_redacted(self) -> None:
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc.def"
        out = secret_redaction.redact(text)
        assert "eyJ" not in out
        assert "<REDACTED:" in out

    def test_doppler_token_redacted(self) -> None:
        text = "DOPPLER_TOKEN=dp.st.prd.ABCDEF1234567890abcdef1234567890"
        out = secret_redaction.redact(text)
        assert "dp.st." not in out
        assert "<REDACTED:" in out

    def test_aws_access_key_redacted(self) -> None:
        text = "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
        out = secret_redaction.redact(text)
        assert "AKIA" not in out

    def test_url_userinfo_redacted(self) -> None:
        text = "Connecting to https://admin:hunter2@db.example.com/postgres"
        out = secret_redaction.redact(text)
        assert "hunter2" not in out
        assert "admin" not in out

    def test_jwt_redacted(self) -> None:
        text = "token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.aBcDeFgHiJk"
        out = secret_redaction.redact(text)
        assert "eyJ" not in out

    def test_multiple_secrets_all_redacted(self) -> None:
        text = (
            "sk-proj-1234567890abcdef1234567890abcdef1234567890ab "
            "and dp.st.prd.ABCDEF1234567890abcdef1234567890"
        )
        out = secret_redaction.redact(text)
        assert "sk-proj-" not in out
        assert "dp.st." not in out

    def test_empty_string_unchanged(self) -> None:
        assert secret_redaction.redact("") == ""


class TestHasSecret:
    def test_returns_true_for_known_pattern(self) -> None:
        assert (
            secret_redaction.has_secret(
                "sk-proj-1234567890abcdef1234567890abcdef1234567890ab",
            )
            is True
        )

    def test_returns_false_for_plain_text(self) -> None:
        assert secret_redaction.has_secret("Hello world, no secrets here.") is False


class TestRedactMapping:
    def test_redacts_values_with_sensitive_keys(self) -> None:
        out = secret_redaction.redact_mapping(
            {
                "user": "alice",
                "api_key": "anything-here-should-be-redacted",
                "password": "hunter2",
                "token": "value-regardless-of-format",
            },
        )
        assert out["user"] == "alice"
        assert "anything-here" not in out["api_key"]
        assert out["api_key"].startswith("<REDACTED:")
        assert "hunter2" not in out["password"]
        assert "value-regardless" not in out["token"]

    def test_sensitive_key_detection_is_case_insensitive(self) -> None:
        out = secret_redaction.redact_mapping({"API_KEY": "leak", "Password": "x"})
        assert "leak" not in out["API_KEY"]
        assert out["Password"].startswith("<REDACTED:")

    def test_non_sensitive_keys_still_scan_value_for_patterns(self) -> None:
        out = secret_redaction.redact_mapping(
            {"message": "got key sk-proj-1234567890abcdef1234567890abcdef1234567890ab"},
        )
        assert "sk-proj-" not in out["message"]

    def test_nested_mappings_redacted(self) -> None:
        out = secret_redaction.redact_mapping(
            {
                "outer": {
                    "inner_api_key": "secret-val",
                    "safe": "ok",
                },
            },
        )
        assert out["outer"]["inner_api_key"].startswith("<REDACTED:")
        assert out["outer"]["safe"] == "ok"

    def test_lists_redacted(self) -> None:
        out = secret_redaction.redact_mapping(
            {"values": ["ok", "sk-proj-1234567890abcdef1234567890abcdef1234567890ab"]},
        )
        assert out["values"][0] == "ok"
        assert "sk-proj-" not in out["values"][1]

    def test_non_string_values_untouched(self) -> None:
        out = secret_redaction.redact_mapping({"count": 42, "enabled": True})
        assert out == {"count": 42, "enabled": True}

    def test_original_mapping_not_mutated(self) -> None:
        original = {"api_key": "leak"}
        secret_redaction.redact_mapping(original)
        assert original == {"api_key": "leak"}


class TestSensitiveKeyNames:
    def test_covers_expected_names(self) -> None:
        required = {"api_key", "password", "token", "secret", "authorization"}
        assert required <= secret_redaction.SENSITIVE_KEY_NAMES


@pytest.mark.parametrize(
    "label",
    [
        "openai",
        "bearer",
        "doppler",
        "aws",
        "jwt",
        "url-userinfo",
    ],
)
def test_redaction_labels_are_reported(label: str) -> None:
    # Sanity-check that every supported pattern produces a labelled <REDACTED:...> marker.
    samples = {
        "openai": "sk-proj-1234567890abcdef1234567890abcdef1234567890ab",
        "bearer": "Bearer abcdef1234567890abcdef1234567890abcdef1234",
        "doppler": "dp.st.prd.ABCDEF1234567890abcdef1234567890",
        "aws": "AKIAIOSFODNN7EXAMPLE",
        "jwt": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.aBcDeFgHiJk",
        "url-userinfo": "https://admin:hunter2@db.example.com/",
    }
    out = secret_redaction.redact(samples[label])
    assert "<REDACTED:" in out
    assert label in out
