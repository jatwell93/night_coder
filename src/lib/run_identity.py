"""Run identifiers and canonical UTC timestamps.

Every overnight run carries an opaque ``run_id`` of the form::

    run-YYYYMMDDTHHMMSSZ-<8-hex-suffix>

The timestamp prefix is deterministic and sortable; the suffix guarantees
uniqueness even when two runs start within the same second (e.g. manual
override firing while the timer is also active).

All timestamp helpers in this module refuse naive or non-UTC datetimes —
pilot services work exclusively in UTC to keep traces, manifests, and scenario
evidence directly comparable across timezones.
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime

__all__ = [
    "from_iso8601",
    "new_run_id",
    "to_iso8601",
    "utc_now",
]

_RUN_ID_TIMESTAMP_FMT = "%Y%m%dT%H%M%SZ"
_ISO_FMT = "%Y-%m-%dT%H:%M:%SZ"
_SUFFIX_BYTES = 4


def utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC ``datetime``."""
    return datetime.now(tz=UTC)


def new_run_id(now: datetime | None = None) -> str:
    """Return a new run identifier.

    Parameters
    ----------
    now:
        Timezone-aware UTC datetime. Defaults to :func:`utc_now`. Passing a
        fixed value is useful for tests and for replaying a run with a known
        start time.

    Raises
    ------
    ValueError
        If ``now`` is naive (no ``tzinfo``) or carries a non-UTC offset.
    """
    moment = now if now is not None else utc_now()
    _require_utc(moment, field="now")
    timestamp = moment.strftime(_RUN_ID_TIMESTAMP_FMT)
    suffix = secrets.token_hex(_SUFFIX_BYTES)
    return f"run-{timestamp}-{suffix}"


def to_iso8601(dt: datetime) -> str:
    """Format a UTC datetime as ``YYYY-MM-DDTHH:MM:SSZ`` (second precision)."""
    _require_utc(dt, field="dt")
    return dt.strftime(_ISO_FMT)


def from_iso8601(value: str) -> datetime:
    """Parse an ISO 8601 UTC timestamp.

    Accepts either the ``Z`` suffix or the explicit ``+00:00`` offset. Any
    other offset is rejected — the pilot stores only UTC timestamps.
    """
    normalised = value.replace("Z", "+00:00") if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalised)
    _require_utc(parsed, field="value")
    return parsed


def _require_utc(dt: datetime, *, field: str) -> None:
    if dt.tzinfo is None:
        msg = f"{field} must be timezone-aware; got naive datetime {dt!r}"
        raise ValueError(msg)
    offset = dt.utcoffset()
    if offset is None or offset.total_seconds() != 0:
        msg = f"{field} must be UTC (offset 0); got {dt!r}"
        raise ValueError(msg)
