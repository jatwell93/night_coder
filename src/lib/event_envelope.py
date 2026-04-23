"""Structured telemetry event envelope.

Every event emitted by the system — execution progress, guardrail blocks,
judge outcomes, memory operations, system-level notices — shares this
envelope. Consumers (telemetry publisher T040, run manifest builder T041,
morning review assembler T054) rely on the envelope being stable.

The envelope is intentionally small: five required fields plus an optional
``payload_ref`` pointing at the full payload on disk. Keeping it small means
event logs stay cheap to parse line-by-line and secret-redaction (T065) only
has to inspect a bounded set of fields.

See ``docs/superpowers/pilot/runbooks/reason-codes.md`` for the reason-code
vocabulary this envelope carries.
"""

from __future__ import annotations

import json
import re
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from lib.run_identity import to_iso8601, utc_now

__all__ = [
    "EventEnvelope",
    "EventType",
    "Severity",
    "new_envelope",
]

_EVENT_ID_TIMESTAMP_FMT = "%Y%m%dT%H%M%SZ"
_EVENT_ID_SUFFIX_BYTES = 4
_REASON_CODE_PATTERN = re.compile(r"^[A-Z]{2,4}\.[a-z]+\.[a-z0-9][a-z0-9-]*$")


class EventType(str, Enum):
    """Canonical event type — matches data-model.md §7 enum exactly."""

    EXECUTION = "execution"
    GUARDRAIL = "guardrail"
    JUDGE = "judge"
    MEMORY = "memory"
    SYSTEM = "system"


class Severity(str, Enum):
    """Event severity — matches status-taxonomy.md §4 exactly."""

    INFO = "info"
    WARN = "warn"
    ERROR = "error"


@dataclass(frozen=True)
class EventEnvelope:
    """Immutable telemetry event.

    Construct via :func:`new_envelope` rather than directly — the factory
    handles id generation, timestamp defaults, and validation.
    """

    event_id: str
    run_id: str
    event_type: EventType
    severity: Severity
    reason_code: str
    timestamp: datetime
    payload_ref: str | None = field(default=None)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dict with enum values as strings."""
        out: dict[str, Any] = {
            "event_id": self.event_id,
            "run_id": self.run_id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "reason_code": self.reason_code,
            "timestamp": to_iso8601(self.timestamp),
        }
        if self.payload_ref is not None:
            out["payload_ref"] = self.payload_ref
        return out

    def to_json(self) -> str:
        """Return a single-line JSON representation suitable for ``events.jsonl``."""
        return json.dumps(self.to_dict(), separators=(",", ":"))


def new_envelope(
    *,
    run_id: str,
    event_type: EventType,
    severity: Severity,
    reason_code: str,
    timestamp: datetime | None = None,
    payload_ref: str | None = None,
) -> EventEnvelope:
    """Create a new :class:`EventEnvelope` with validation."""
    if not run_id:
        msg = "run_id must be non-empty"
        raise ValueError(msg)

    if not reason_code or not _REASON_CODE_PATTERN.match(reason_code):
        msg = (
            f"reason_code {reason_code!r} must match "
            "<NAMESPACE>.<category>.<specific-reason> (see reason-codes.md)"
        )
        raise ValueError(msg)

    moment = timestamp if timestamp is not None else utc_now()
    # Reuse run_identity's UTC enforcement by calling to_iso8601 — it raises if
    # the datetime is naive or non-UTC, which is exactly what we want here.
    to_iso8601(moment)

    event_id = _new_event_id(moment)
    return EventEnvelope(
        event_id=event_id,
        run_id=run_id,
        event_type=event_type,
        severity=severity,
        reason_code=reason_code,
        timestamp=moment,
        payload_ref=payload_ref,
    )


def _new_event_id(moment: datetime) -> str:
    stamp = moment.strftime(_EVENT_ID_TIMESTAMP_FMT)
    suffix = secrets.token_hex(_EVENT_ID_SUFFIX_BYTES)
    return f"evt-{stamp}-{suffix}"
