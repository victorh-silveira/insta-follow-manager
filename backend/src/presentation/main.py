"""FastAPI application entrypoint."""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.application.event_logger import emit_event
from src.domain.exceptions import (
    ChallengeRequiredError,
    GatewayAuthError,
    GatewayError,
    NotFollowerError,
    NotFollowingError,
    ProfileNotFoundError,
    RateLimitError,
    TwoFactorRequiredError,
)
from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging.semantic_logger import configure_logging
from src.presentation.api.middleware.request_logging import RequestLoggingMiddleware
from src.presentation.api.routes.auth import router as auth_router
from src.presentation.api.routes.health import router as health_router
from src.presentation.api.routes.relationships import router as relationships_router

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    configure_logging(level=settings.log_level, fmt=settings.log_format)

    app = FastAPI(
        title="Insta Follow Manager API",
        version="1.0.0",
        description="Clean Architecture + DDD backend for Instagram follow/unfollow triage.",
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _register_exception_handlers(app)
    app.include_router(auth_router)
    app.include_router(health_router)
    app.include_router(relationships_router)
    return app


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ProfileNotFoundError)
    async def handle_not_found(_: Request, exc: ProfileNotFoundError) -> JSONResponse:
        emit_event(logger, logging.WARNING, "api.domain_error", str(exc), error="ProfileNotFoundError")
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(NotFollowingError)
    async def handle_not_following(_: Request, exc: NotFollowingError) -> JSONResponse:
        emit_event(logger, logging.WARNING, "api.domain_error", str(exc), error="NotFollowingError")
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(NotFollowerError)
    async def handle_not_follower(_: Request, exc: NotFollowerError) -> JSONResponse:
        emit_event(logger, logging.WARNING, "api.domain_error", str(exc), error="NotFollowerError")
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(TwoFactorRequiredError)
    async def handle_two_factor(_: Request, exc: TwoFactorRequiredError) -> JSONResponse:
        emit_event(logger, logging.WARNING, "api.two_factor_required", str(exc))
        return JSONResponse(status_code=401, content={"detail": str(exc), "requires_2fa": True})

    @app.exception_handler(ChallengeRequiredError)
    async def handle_challenge(_: Request, exc: ChallengeRequiredError) -> JSONResponse:
        emit_event(logger, logging.WARNING, "api.challenge_required", str(exc))
        return JSONResponse(status_code=401, content={"detail": str(exc), "requires_challenge": True})

    @app.exception_handler(GatewayAuthError)
    async def handle_auth_error(_: Request, exc: GatewayAuthError) -> JSONResponse:
        emit_event(logger, logging.ERROR, "api.gateway_auth_error", str(exc))
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(RateLimitError)
    async def handle_rate_limit(_: Request, exc: RateLimitError) -> JSONResponse:
        emit_event(logger, logging.WARNING, "api.rate_limit", str(exc))
        return JSONResponse(status_code=429, content={"detail": str(exc)})

    @app.exception_handler(GatewayError)
    async def handle_gateway_error(_: Request, exc: GatewayError) -> JSONResponse:
        emit_event(logger, logging.ERROR, "api.gateway_error", str(exc))
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def handle_value_error(_: Request, exc: ValueError) -> JSONResponse:
        emit_event(logger, logging.WARNING, "api.validation_error", str(exc))
        return JSONResponse(status_code=422, content={"detail": str(exc)})


app = create_app()
