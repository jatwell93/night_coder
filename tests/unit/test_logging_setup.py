"""Tests for src/lib/logging_setup.py."""

from __future__ import annotations

import io
import json
import logging

import pytest

from lib import logging_setup


@pytest.fixture(autouse=True)
def _reset_root_logger() -> None:
    # Ensure each test starts with a clean root logger so handler assertions
    # aren't polluted by earlier ``configure_logging`` calls.
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    root.setLevel(logging.WARNING)


def _capture_stream() -> io.StringIO:
    return io.StringIO()


def _night_coder_handlers() -> list[logging.Handler]:
    return [h for h in logging.getLogger().handlers if getattr(h, "_night_coder_handler", False)]


class TestConfigure:
    def test_adds_a_single_handler(self) -> None:
        stream = _capture_stream()
        logging_setup.configure_logging(level="INFO", stream=stream)
        assert len(_night_coder_handlers()) == 1

    def test_idempotent_repeated_calls(self) -> None:
        stream = _capture_stream()
        logging_setup.configure_logging(level="INFO", stream=stream)
        logging_setup.configure_logging(level="INFO", stream=stream)
        assert len(_night_coder_handlers()) == 1

    def test_level_applied(self) -> None:
        stream = _capture_stream()
        logging_setup.configure_logging(level="DEBUG", stream=stream)
        assert logging.getLogger().level == logging.DEBUG


class TestJsonOutput:
    def _emit(
        self,
        *,
        message: str,
        stream: io.StringIO,
        run_id: str | None = None,
        extra: dict[str, object] | None = None,
    ) -> dict[str, object]:
        logging_setup.configure_logging(level="INFO", stream=stream, run_id=run_id)
        logger = logging.getLogger("night_coder.test")
        logger.info(message, extra=extra or {})
        stream.seek(0)
        line = stream.readline().strip()
        return json.loads(line)

    def test_emits_valid_json_line(self) -> None:
        stream = _capture_stream()
        record = self._emit(message="hello", stream=stream)
        assert record["message"] == "hello"
        assert record["level"] == "INFO"
        assert record["logger"] == "night_coder.test"

    def test_includes_timestamp_utc(self) -> None:
        stream = _capture_stream()
        record = self._emit(message="hi", stream=stream)
        assert isinstance(record["timestamp"], str)
        assert record["timestamp"].endswith("Z")

    def test_includes_run_id_when_provided(self) -> None:
        stream = _capture_stream()
        record = self._emit(
            message="hi",
            stream=stream,
            run_id="run-20260423T130000Z-deadbeef",
        )
        assert record["run_id"] == "run-20260423T130000Z-deadbeef"

    def test_omits_run_id_when_not_provided(self) -> None:
        stream = _capture_stream()
        record = self._emit(message="hi", stream=stream)
        assert "run_id" not in record

    def test_includes_extra_fields(self) -> None:
        stream = _capture_stream()
        record = self._emit(
            message="hi",
            stream=stream,
            extra={"scenario_id": "SCN-001"},
        )
        assert record["scenario_id"] == "SCN-001"


class TestRedaction:
    def _emit_line(self, *, message: str, stream: io.StringIO) -> str:
        logging_setup.configure_logging(level="INFO", stream=stream)
        logging.getLogger("night_coder.test").info(message)
        stream.seek(0)
        return stream.readline()

    def test_secrets_in_message_are_redacted(self) -> None:
        stream = _capture_stream()
        line = self._emit_line(
            message="key=sk-proj-1234567890abcdef1234567890abcdef1234567890ab",
            stream=stream,
        )
        assert "sk-proj-" not in line
        assert "<REDACTED:" in line

    def test_secrets_in_extra_fields_are_redacted(self) -> None:
        stream = _capture_stream()
        logging_setup.configure_logging(level="INFO", stream=stream)
        logging.getLogger("night_coder.test").info(
            "event",
            extra={"api_key": "raw-key-value", "safe": "ok"},
        )
        stream.seek(0)
        record = json.loads(stream.readline())
        assert record["api_key"].startswith("<REDACTED:")
        assert record["safe"] == "ok"


class TestStderrIsSensibleDefault:
    def test_default_stream_is_stderr(self) -> None:
        import sys

        logging_setup.configure_logging(level="INFO")
        handlers = _night_coder_handlers()
        assert len(handlers) == 1
        handler = handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert handler.stream is sys.stderr
