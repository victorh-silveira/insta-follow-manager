"""Unit tests for semantic structured logging and context correlation."""

import json
import logging

from src.application.event_logger import emit_event
from src.infrastructure.logging.context import (
    get_request_id,
    reset_request_id,
    set_request_id,
)
from src.infrastructure.logging.semantic_logger import (
    SemanticConsoleFormatter,
    SemanticJsonFormatter,
)


def _build_record(event: str, message: str, **fields: object) -> logging.LogRecord:
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=message,
        args=(),
        exc_info=None,
    )
    record.event = event
    record.fields = fields
    return record


def test_json_formatter_includes_semantic_fields_and_request_id() -> None:
    token = set_request_id("req-abc-123")
    try:
        record = _build_record(
            "relationships.unfollow.succeeded",
            "Profile unfollowed",
            pk="102",
            username="artur_foto",
            bucket="A",
        )
        formatted = SemanticJsonFormatter().format(record)
        payload = json.loads(formatted)

        assert payload["level"] == "INFO"
        assert payload["event"] == "relationships.unfollow.succeeded"
        assert payload["message"] == "Profile unfollowed"
        assert payload["request_id"] == "req-abc-123"
        assert payload["pk"] == "102"
        assert payload["username"] == "artur_foto"
        assert payload["bucket"] == "A"
        assert "timestamp" in payload
    finally:
        reset_request_id(token)

    assert get_request_id() is None


def test_json_formatter_redacts_sensitive_credentials() -> None:
    record = _build_record(
        "gateway.auth.debug",
        "Attempting login",
        username="user_test",
        ig_password="super-secret-password",
        session_token="tok-123",
    )
    payload = json.loads(SemanticJsonFormatter().format(record))

    assert payload["username"] == "user_test"
    assert payload["ig_password"] == "***REDACTED***"
    assert payload["session_token"] == "***REDACTED***"


def test_console_formatter_outputs_key_value_without_emojis() -> None:
    token = set_request_id("req-console-1")
    try:
        record = _build_record(
            "relationships.sync.completed",
            "Sync finished",
            following_count=26,
        )
        line = SemanticConsoleFormatter().format(record)

        assert "event=relationships.sync.completed" in line
        assert "request_id=req-console-1" in line
        assert "following_count=26" in line
        assert "Sync finished" in line
    finally:
        reset_request_id(token)


def test_emit_event_passes_extra_fields(caplog: object) -> None:
    logger = logging.getLogger("test.emit")
    with caplog.at_level(logging.INFO):  # type: ignore[attr-defined]
        emit_event(logger, logging.INFO, "test.event", "Hello", count=3)
    assert len(caplog.records) == 1  # type: ignore[attr-defined]
    assert caplog.records[0].event == "test.event"  # type: ignore[attr-defined]
    assert caplog.records[0].fields == {"count": 3}  # type: ignore[attr-defined]


def test_json_formatter_includes_exception_traceback() -> None:
    try:
        raise RuntimeError("sample failure")
    except RuntimeError as exc:
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="Failed",
            args=(),
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        record.event = "test.failed"
        record.fields = {}
        payload = json.loads(SemanticJsonFormatter().format(record))
        assert "RuntimeError: sample failure" in payload["exception"]
