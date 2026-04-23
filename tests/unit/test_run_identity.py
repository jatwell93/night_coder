"""Tests for src/lib/run_identity.py."""

from __future__ import annotations

import re
from datetime import UTC, datetime

import pytest

from lib import run_identity

RUN_ID_PATTERN = re.compile(
    r"^run-\d{8}T\d{6}Z-[0-9a-f]{8}$",
)


class TestNewRunId:
    def test_format_matches_pattern(self) -> None:
        run_id = run_identity.new_run_id()
        assert RUN_ID_PATTERN.match(run_id), f"run_id {run_id!r} does not match pattern"

    def test_uses_utc_timestamp_from_argument(self) -> None:
        fixed = datetime(2026, 4, 23, 14, 30, 5, tzinfo=UTC)
        run_id = run_identity.new_run_id(now=fixed)
        assert run_id.startswith("run-20260423T143005Z-")

    def test_rejects_naive_datetime(self) -> None:
        naive = datetime(2026, 4, 23, 14, 30, 5)
        with pytest.raises(ValueError, match="timezone-aware"):
            run_identity.new_run_id(now=naive)

    def test_rejects_non_utc_timezone(self) -> None:
        from datetime import timedelta, timezone

        plus_ten = timezone(timedelta(hours=10))
        aest = datetime(2026, 4, 23, 14, 30, 5, tzinfo=plus_ten)
        with pytest.raises(ValueError, match="UTC"):
            run_identity.new_run_id(now=aest)

    def test_two_calls_produce_different_ids(self) -> None:
        fixed = datetime(2026, 4, 23, 14, 30, 5, tzinfo=UTC)
        a = run_identity.new_run_id(now=fixed)
        b = run_identity.new_run_id(now=fixed)
        assert a != b, "suffix must differ even with identical timestamps"


class TestUtcNow:
    def test_returns_timezone_aware_utc(self) -> None:
        now = run_identity.utc_now()
        assert now.tzinfo is not None
        assert now.utcoffset() == (now - now).__class__(0)


class TestIsoRoundTrip:
    def test_to_iso8601_uses_z_suffix(self) -> None:
        dt = datetime(2026, 4, 23, 14, 30, 5, tzinfo=UTC)
        assert run_identity.to_iso8601(dt) == "2026-04-23T14:30:05Z"

    def test_to_iso8601_strips_subsecond_precision_by_default(self) -> None:
        dt = datetime(2026, 4, 23, 14, 30, 5, 123456, tzinfo=UTC)
        assert run_identity.to_iso8601(dt) == "2026-04-23T14:30:05Z"

    def test_to_iso8601_rejects_naive(self) -> None:
        with pytest.raises(ValueError, match="timezone-aware"):
            run_identity.to_iso8601(datetime(2026, 4, 23, 14, 30, 5))

    def test_from_iso8601_parses_z_suffix(self) -> None:
        parsed = run_identity.from_iso8601("2026-04-23T14:30:05Z")
        assert parsed == datetime(2026, 4, 23, 14, 30, 5, tzinfo=UTC)

    def test_from_iso8601_parses_offset(self) -> None:
        parsed = run_identity.from_iso8601("2026-04-23T14:30:05+00:00")
        assert parsed == datetime(2026, 4, 23, 14, 30, 5, tzinfo=UTC)

    def test_round_trip(self) -> None:
        dt = datetime(2026, 4, 23, 14, 30, 5, tzinfo=UTC)
        assert run_identity.from_iso8601(run_identity.to_iso8601(dt)) == dt

    def test_from_iso8601_rejects_non_utc(self) -> None:
        with pytest.raises(ValueError, match="UTC"):
            run_identity.from_iso8601("2026-04-23T14:30:05+10:00")
