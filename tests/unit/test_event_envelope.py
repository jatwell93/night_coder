"""Tests for src/lib/event_envelope.py."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime

import pytest

from lib import event_envelope
from lib.event_envelope import EventEnvelope, EventType, Severity

RUN_ID = "run-20260423T130000Z-deadbeef"


class TestEnums:
    def test_event_type_values(self) -> None:
        assert {t.value for t in EventType} == {
            "execution",
            "guardrail",
            "judge",
            "memory",
            "system",
        }

    def test_severity_values(self) -> None:
        assert {s.value for s in Severity} == {"info", "warn", "error"}


class TestNewEnvelope:
    def test_auto_generates_event_id(self) -> None:
        env = event_envelope.new_envelope(
            run_id=RUN_ID,
            event_type=EventType.EXECUTION,
            severity=Severity.INFO,
            reason_code="RUN.start.ok",
        )
        assert env.event_id.startswith("evt-")
        assert re.match(r"^evt-\d{8}T\d{6}Z-[0-9a-f]{8}$", env.event_id)

    def test_auto_generates_utc_timestamp(self) -> None:
        env = event_envelope.new_envelope(
            run_id=RUN_ID,
            event_type=EventType.EXECUTION,
            severity=Severity.INFO,
            reason_code="RUN.start.ok",
        )
        assert env.timestamp.tzinfo is not None
        assert env.timestamp.utcoffset() == (env.timestamp - env.timestamp).__class__(0)

    def test_accepts_optional_payload_ref(self) -> None:
        env = event_envelope.new_envelope(
            run_id=RUN_ID,
            event_type=EventType.GUARDRAIL,
            severity=Severity.WARN,
            reason_code="GRD.block.destructive-filesystem",
            payload_ref="runs/X/events/payload-42.json",
        )
        assert env.payload_ref == "runs/X/events/payload-42.json"

    def test_rejects_empty_reason_code(self) -> None:
        with pytest.raises(ValueError, match="reason_code"):
            event_envelope.new_envelope(
                run_id=RUN_ID,
                event_type=EventType.EXECUTION,
                severity=Severity.INFO,
                reason_code="",
            )

    def test_rejects_malformed_reason_code(self) -> None:
        with pytest.raises(ValueError, match="reason_code"):
            event_envelope.new_envelope(
                run_id=RUN_ID,
                event_type=EventType.EXECUTION,
                severity=Severity.INFO,
                reason_code="no-namespace",
            )

    def test_rejects_empty_run_id(self) -> None:
        with pytest.raises(ValueError, match="run_id"):
            event_envelope.new_envelope(
                run_id="",
                event_type=EventType.EXECUTION,
                severity=Severity.INFO,
                reason_code="RUN.start.ok",
            )


class TestTimestampOverride:
    def test_accepts_utc_datetime(self) -> None:
        when = datetime(2026, 4, 23, 13, 0, 0, tzinfo=UTC)
        env = event_envelope.new_envelope(
            run_id=RUN_ID,
            event_type=EventType.EXECUTION,
            severity=Severity.INFO,
            reason_code="RUN.start.ok",
            timestamp=when,
        )
        assert env.timestamp == when

    def test_rejects_naive_datetime(self) -> None:
        naive = datetime(2026, 4, 23, 13, 0, 0)
        with pytest.raises(ValueError, match="timezone-aware"):
            event_envelope.new_envelope(
                run_id=RUN_ID,
                event_type=EventType.EXECUTION,
                severity=Severity.INFO,
                reason_code="RUN.start.ok",
                timestamp=naive,
            )


class TestSerialization:
    def _sample(self) -> EventEnvelope:
        return event_envelope.new_envelope(
            run_id=RUN_ID,
            event_type=EventType.JUDGE,
            severity=Severity.INFO,
            reason_code="JDG.satisfied.ok",
            timestamp=datetime(2026, 4, 23, 13, 42, 0, tzinfo=UTC),
            payload_ref="runs/X/verdicts/SCN-001.json",
        )

    def test_to_dict_has_required_fields(self) -> None:
        d = self._sample().to_dict()
        assert d.keys() >= {
            "event_id",
            "run_id",
            "event_type",
            "severity",
            "reason_code",
            "timestamp",
            "payload_ref",
        }

    def test_to_dict_serializes_enums_as_strings(self) -> None:
        d = self._sample().to_dict()
        assert d["event_type"] == "judge"
        assert d["severity"] == "info"

    def test_to_dict_serializes_timestamp_as_iso_utc(self) -> None:
        d = self._sample().to_dict()
        assert d["timestamp"] == "2026-04-23T13:42:00Z"

    def test_to_json_is_parseable(self) -> None:
        s = self._sample().to_json()
        parsed = json.loads(s)
        assert parsed["run_id"] == RUN_ID

    def test_to_dict_omits_null_payload_ref(self) -> None:
        env = event_envelope.new_envelope(
            run_id=RUN_ID,
            event_type=EventType.SYSTEM,
            severity=Severity.INFO,
            reason_code="SYS.config.loaded",
        )
        assert "payload_ref" not in env.to_dict()
