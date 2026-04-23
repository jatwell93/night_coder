"""Redact secrets from log lines, trace payloads, and event envelopes.

This is a **last-resort** defence. Services should not put secrets into
telemetry in the first place — Doppler injects them into the process
environment at runtime and they stay there. But when string interpolation
accidentally captures one, this filter catches the obvious patterns before
data reaches a log file or trace backend.

Two surfaces:

- :func:`redact` — pattern-based scan of arbitrary strings.
- :func:`redact_mapping` — recursive scan of nested dict/list structures,
  adding **key-name awareness** (``api_key``, ``password``, etc. are always
  redacted regardless of the value's format).

Each redaction replaces the match with ``<REDACTED:<label>>`` so operators can
see at a glance what kind of secret was suppressed.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

__all__ = [
    "SENSITIVE_KEY_NAMES",
    "has_secret",
    "redact",
    "redact_mapping",
]


# Keys whose *values* are always redacted regardless of the value's contents.
# Match is case-insensitive and matches any key whose name contains one of
# these substrings.
SENSITIVE_KEY_NAMES: frozenset[str] = frozenset(
    {
        "api_key",
        "apikey",
        "auth",
        "authorization",
        "credential",
        "password",
        "passwd",
        "private_key",
        "secret",
        "token",
    },
)


# (label, pattern) pairs. Order matters: more-specific patterns first.
_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # URL user-info (https://user:pass@host) — scan before JWT so we strip
    # credentials out of connection strings intact.
    (
        "url-userinfo",
        re.compile(r"(?P<scheme>https?://)[^\s/@:]+:[^\s/@]+@"),
    ),
    # OpenAI-style keys (``sk-proj-...``, ``sk-...``).
    (
        "openai",
        re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    ),
    # Doppler service tokens: ``dp.st.<env>.<token>``.
    (
        "doppler",
        re.compile(r"\bdp\.st\.[A-Za-z0-9_]+\.[A-Za-z0-9_-]{20,}\b"),
    ),
    # AWS access key id.
    (
        "aws",
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    ),
    # Bearer tokens after an explicit ``Bearer `` prefix.
    (
        "bearer",
        re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-+/=]{16,}\b"),
    ),
    # JWT: three dot-separated base64url segments starting with ``eyJ``.
    (
        "jwt",
        re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
    ),
)


def redact(text: str) -> str:
    """Return ``text`` with known secret patterns replaced by ``<REDACTED:label>``."""
    if not text:
        return text
    result = text
    for label, pattern in _PATTERNS:
        result = _apply_pattern(result, label, pattern)
    return result


def has_secret(text: str) -> bool:
    """Return ``True`` if any known secret pattern matches ``text``."""
    if not text:
        return False
    return any(pattern.search(text) for _, pattern in _PATTERNS)


def redact_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively redact a mapping, returning a new dict.

    Values under keys whose name contains a substring in
    :data:`SENSITIVE_KEY_NAMES` are wholly replaced with
    ``<REDACTED:sensitive-key>``. Other string values are scanned via
    :func:`redact`. Nested mappings and lists are traversed.
    """
    result = _redact_any(data)
    assert isinstance(result, dict)
    return result


def _redact_any(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {k: _redact_value_for_key(k, v) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_any(item) for item in value]
    if isinstance(value, str):
        return redact(value)
    return value


def _redact_value_for_key(key: str, value: Any) -> Any:
    if isinstance(key, str) and _is_sensitive_key(key):
        return "<REDACTED:sensitive-key>"
    return _redact_any(value)


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(name in lowered for name in SENSITIVE_KEY_NAMES)


def _apply_pattern(text: str, label: str, pattern: re.Pattern[str]) -> str:
    if label == "url-userinfo":
        # Preserve the scheme so operators still see the target host context.
        return pattern.sub(rf"\g<scheme><REDACTED:{label}>@", text)
    return pattern.sub(f"<REDACTED:{label}>", text)
