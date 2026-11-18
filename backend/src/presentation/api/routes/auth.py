"""REST endpoints for Instagram authentication and session lifecycle."""

from dataclasses import asdict

from fastapi import APIRouter, Depends

from src.application.use_cases.auth_instagram import (
    GetAuthStatusUseCase,
    LoginInstagramUseCase,
    LogoutInstagramUseCase,
)
from src.presentation.api.dependencies import (
    get_auth_status_use_case,
    get_login_use_case,
    get_logout_use_case,
)
from src.presentation.api.schemas import AuthStatusResponse, LoginRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/status", response_model=AuthStatusResponse)
def get_auth_status(
    use_case: GetAuthStatusUseCase = Depends(get_auth_status_use_case),
) -> AuthStatusResponse:
    """Return active Instagram session status."""
    return AuthStatusResponse(**asdict(use_case.execute()))


@router.post("/login", response_model=AuthStatusResponse)
def login_instagram(
    payload: LoginRequest,
    use_case: LoginInstagramUseCase = Depends(get_login_use_case),
) -> AuthStatusResponse:
    """Authenticate against Instagram API and persist session.json."""
    result = use_case.execute(
        username=payload.username,
        password=payload.password,
        verification_code=payload.verification_code,
        challenge_code=payload.challenge_code,
        session_id=payload.session_id,
    )
    return AuthStatusResponse(**asdict(result))


@router.post("/logout", response_model=AuthStatusResponse)
def logout_instagram(
    use_case: LogoutInstagramUseCase = Depends(get_logout_use_case),
) -> AuthStatusResponse:
    """Clear active Instagram session."""
    return AuthStatusResponse(**asdict(use_case.execute()))
