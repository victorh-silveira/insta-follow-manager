"""Context variables for request-scoped correlation IDs."""

from contextvars import ContextVar, Token

_request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    """Return the current request correlation ID, if set."""
    return _request_id_var.get()


def set_request_id(request_id: str) -> Token[str | None]:
    """Bind a correlation ID to the current execution context."""
    return _request_id_var.set(request_id)


def reset_request_id(token: Token[str | None]) -> None:
    """Restore the previous correlation ID context."""
    _request_id_var.reset(token)
