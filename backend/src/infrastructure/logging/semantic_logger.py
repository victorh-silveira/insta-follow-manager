"""Structured semantic logging formatters and configuration (stdout/stderr)."""

from datetime import UTC, datetime
import json
import logging
import sys
from typing import Any

from src.infrastructure.logging.context import get_request_id

_SENSITIVE_KEYS = frozenset(
    {"password", "ig_password", "token", "secret", "cookie", "session", "authorization"}
)


def _redact_fields(fields: dict[str, Any]) -> dict[str, Any]:
    """Mask any sensitive credential keys before emitting logs."""
    sanitized: dict[str, Any] = {}
    for key, value in fields.items():
        if any(sensitive in key.casefold() for sensitive in _SENSITIVE_KEYS):
            sanitized[key] = "***REDACTED***"
        else:
            sanitized[key] = value
    return sanitized


def _extract_payload(record: logging.LogRecord) -> dict[str, Any]:
    timestamp = datetime.fromtimestamp(record.created, tz=UTC).isoformat()
    event = getattr(record, "event", "app.log")
    raw_fields = getattr(record, "fields", None)
    fields = _redact_fields(raw_fields) if isinstance(raw_fields, dict) else {}

    payload: dict[str, Any] = {
        "timestamp": timestamp,
        "level": record.levelname,
        "logger": record.name,
        "event": event,
        "message": record.getMessage(),
        "request_id": get_request_id(),
        **fields,
    }
    if record.exc_info:
        payload["exception"] = logging.Formatter().formatException(record.exc_info)
    return payload


class SemanticJsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects for log aggregators."""

    def format(self, record: logging.LogRecord) -> str:
        payload = _extract_payload(record)
        return json.dumps(payload, ensure_ascii=False, default=str)


class SemanticConsoleFormatter(logging.Formatter):
    """Formats log records as key=value lines for local development."""

    def format(self, record: logging.LogRecord) -> str:
        payload = _extract_payload(record)
        timestamp = payload.pop("timestamp")
        level = payload.pop("level")
        event = payload.pop("event")
        message = payload.pop("message")
        logger_name = payload.pop("logger")
        request_id = payload.pop("request_id")

        kv_parts = [f"event={event}", f"logger={logger_name}"]
        if request_id:
            kv_parts.append(f"request_id={request_id}")
        for key, value in payload.items():
            kv_parts.append(f"{key}={value!r}" if isinstance(value, str) else f"{key}={value}")

        return f"{timestamp} | {level:<7} | {' '.join(kv_parts)} | {message}"


def configure_logging(level: str = "INFO", fmt: str = "json") -> None:
    """Configure root logger to emit structured semantic logs to stdout."""
    root = logging.getLogger()
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter: logging.Formatter = (
        SemanticConsoleFormatter() if fmt.lower() == "console" else SemanticJsonFormatter()
    )
    handler.setFormatter(formatter)

    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Avoid duplicate unformatted access logs from uvicorn; handled by RequestLoggingMiddleware.
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False
