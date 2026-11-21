"""Use cases for Instagram authentication and session management."""

import logging

from src.application.dto.profile_dto import AuthStatusDTO
from src.application.event_logger import emit_event
from src.domain.gateways.instagram_gateway import AuthAccount, InstagramGateway

logger = logging.getLogger(__name__)


def _to_dto(account: AuthAccount, gateway_mode: str) -> AuthStatusDTO:
    return AuthStatusDTO(
        authenticated=account.is_authenticated,
        gateway_mode=gateway_mode,
        username=account.username,
        full_name=account.full_name,
        profile_pic_url=account.profile_pic_url,
        biography=account.biography,
        media_count=account.media_count,
        follower_count=account.follower_count,
        following_count=account.following_count,
        is_private=account.is_private,
        is_verified=account.is_verified,
    )


class GetAuthStatusUseCase:
    """Checks current Instagram session status."""

    def __init__(self, gateway: InstagramGateway) -> None:
        self._gateway = gateway

    def execute(self) -> AuthStatusDTO:
        account = self._gateway.get_auth_status()
        return _to_dto(account, self._gateway.mode_name)


class LoginInstagramUseCase:
    """Authenticates a user with Instagram and persists session."""

    def __init__(self, gateway: InstagramGateway) -> None:
        self._gateway = gateway

    def execute(
        self,
        username: str = "",
        password: str = "",
        verification_code: str | None = None,
        challenge_code: str | None = None,
        session_id: str | None = None,
    ) -> AuthStatusDTO:
        cleaned_user = username.strip().lstrip("@")
        cleaned_session_id = session_id.strip() if session_id else None
        if not cleaned_session_id and (not cleaned_user or not password):
            raise ValueError("Usuario e senha do Instagram sao obrigatorios.")

        emit_event(
            logger,
            logging.INFO,
            "auth.instagram.login_started",
            "Authenticating Instagram account",
            username=cleaned_user or "sessionid",
            gateway_mode=self._gateway.mode_name,
            auth_method="sessionid" if cleaned_session_id else "credentials",
        )
        account = self._gateway.login(
            username=cleaned_user,
            password=password,
            verification_code=verification_code.strip() if verification_code else None,
            challenge_code=challenge_code.strip() if challenge_code else None,
            session_id=cleaned_session_id,
        )
        emit_event(
            logger,
            logging.INFO,
            "auth.instagram.login_succeeded",
            "Instagram account authenticated",
            username=account.username,
            gateway_mode=self._gateway.mode_name,
        )
        return _to_dto(account, self._gateway.mode_name)


class LogoutInstagramUseCase:
    """Logs out and clears persisted Instagram session."""

    def __init__(self, gateway: InstagramGateway) -> None:
        self._gateway = gateway

    def execute(self) -> AuthStatusDTO:
        self._gateway.logout()
        emit_event(
            logger,
            logging.INFO,
            "auth.instagram.logged_out",
            "Instagram session cleared",
            gateway_mode=self._gateway.mode_name,
        )
        return AuthStatusDTO(
            authenticated=False,
            gateway_mode=self._gateway.mode_name,
        )
