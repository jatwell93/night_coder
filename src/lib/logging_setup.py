"""Structured logger bootstrap with redaction hook.

Installs a single stderr handler on the root logger that:

- formats records as single-line JSON (one record per line, suitable for
  ``events.jsonl``-style ingestion),
- stamps every record with a UTC ISO 8601 timestamp,
- optionally tags every record in the process with a ``run_id``,
- runs :mod:`lib.secret_redaction` over both the rendered message and every
  ``extra`` field so accidentally-included secrets are scrubbed before they
  hit disk or a log aggregator.

Call :func:`configure_logging` exactly once at process startup. Repeated calls
are idempotent — old handlers are removed before the new one is installed so
reconfiguring after, for example, a run id becomes known does not duplicate
output.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from typing import IO, Any

from lib.run_identity import to_iso8601, utc_now
from lib.secret_redaction import redact, redact_mapping

__all__ = ["configure_logging"]

_HANDLER_ATTR = "_night_coder_handler"
_STANDARD_LOGRECORD_ATTRS = frozenset(
    {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "taskName",
        "thread",
        "threadName",
    },
)


class _JsonRedactingFormatter(logging.Formatter):
    """One JSON object per record, with secrets redacted."""

    def __init__(self, *, run_id: str | None = None) -> None:
        super().__init__()
        self._run_id = run_id

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": _format_timestamp(record.created),
            "level": record.levelname,
            "logger": record.name,
            "message": redact(record.getMessage()),
        }
        if self._run_id is not None:
            payload["run_id"] = self._run_id

        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _STANDARD_LOGRECORD_ATTRS and not key.startswith("_")
        }
        if extras:
            redacted = redact_mapping(extras)
            for key, value in redacted.items():
                # Do not let an ``extra`` field silently shadow a core field.
                if key in payload:
                    continue
                payload[key] = value

        if record.exc_info:
            payload["exc_info"] = redact(self.formatException(record.exc_info))

        return json.dumps(payload, separators=(",", ":"), default=str)


def configure_logging(
    *,
    level: int | str = logging.INFO,
    stream: IO[str] | None = None,
    run_id: str | None = None,
) -> None:
    """Install the structured JSON handler on the root logger.

    Parameters
    ----------
    level:
        Root logger level. Accepts either a numeric level or its name (``"INFO"``).
    stream:
        Destination stream. Defaults to :data:`sys.stderr` so stdout remains
        clean for scripted consumption.
    run_id:
        Optional run identifier to stamp on every record emitted after the
        call. Pass ``None`` if the run id is not yet known; call
        :func:`configure_logging` again once it is.
    """
    target = stream if stream is not None else sys.stderr
    handler = logging.StreamHandler(target)
    handler.setFormatter(_JsonRedactingFormatter(run_id=run_id))
    setattr(handler, _HANDLER_ATTR, True)

    root = logging.getLogger()
    root.setLevel(level if isinstance(level, int) else logging.getLevelName(level))
    _remove_previous_night_coder_handlers(root)
    root.addHandler(handler)


def _remove_previous_night_coder_handlers(logger: logging.Logger) -> None:
    for existing in list(logger.handlers):
        if getattr(existing, _HANDLER_ATTR, False):
            logger.removeHandler(existing)


def _format_timestamp(created: float) -> str:
    dt: datetime = utc_now().fromtimestamp(created, tz=utc_now().tzinfo)
    return to_iso8601(dt)
