"""Lightweight semantic event logger helper using Python stdlib logging."""

import logging
from typing import Any


def emit_event(
    logger: logging.Logger,
    level: int,
    event: str,
    message: str,
    **fields: Any,
) -> None:
    """Emit a structured semantic log event with domain context fields."""
    logger.log(level, message, extra={"event": event, "fields": fields})
