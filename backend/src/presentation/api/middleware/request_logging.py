"""HTTP request logging middleware with X-Request-ID correlation."""

from collections.abc import Awaitable, Callable
import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.application.event_logger import emit_event
from src.infrastructure.logging.context import reset_request_id, set_request_id

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Binds a correlation ID per request and emits structured HTTP access logs."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        token = set_request_id(request_id)
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            emit_event(
                logger,
                logging.ERROR,
                "http.request.failed",
                "Unhandled exception during HTTP request",
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
                error_type=type(exc).__name__,
            )
            reset_request_id(token)
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        emit_event(
            logger,
            logging.INFO,
            "http.request.completed",
            "HTTP request processed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        reset_request_id(token)
        return response
