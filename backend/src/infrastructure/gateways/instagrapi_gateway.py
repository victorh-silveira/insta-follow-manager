"""Instagrapi-backed Instagram gateway adapter."""

import logging
from pathlib import Path
from typing import Any

from instagrapi import Client
from instagrapi.exceptions import (
    ChallengeRequired,
    LoginRequired,
    PleaseWaitFewMinutes,
    TwoFactorRequired,
)

from src.application.event_logger import emit_event
from src.domain.exceptions import (
    ChallengeRequiredError,
    GatewayAuthError,
    GatewayError,
    RateLimitError,
    TwoFactorRequiredError,
)
from src.domain.gateways.instagram_gateway import (
    AuthAccount,
    GatewayProfile,
    InstagramGateway,
)

logger = logging.getLogger(__name__)


class InstagrapiGateway(InstagramGateway):
    """Communicates with Instagram Private API via instagrapi with session caching."""

    def __init__(
        self,
        username: str = "",
        password: str = "",
        session_path: str = "./session.json",
    ) -> None:
        self._username = username
        self._password = password
        self._session_path = Path(session_path)
        self._client = Client()
        self._client.delay_range = [1, 3]
        self._authenticated = False
        self._account: AuthAccount | None = None

    @property
    def mode_name(self) -> str:
        return "instagrapi"

    def get_auth_status(self) -> AuthAccount:
        if self._authenticated and self._account is not None:
            return self._account

        if not self._session_path.exists():
            return AuthAccount(is_authenticated=False)

        try:
            self._client.load_settings(self._session_path)
            session_id = getattr(self._client, "sessionid", None)
            if session_id:
                self._client.login_by_sessionid(session_id)
            info = self._client.account_info()
            self._authenticated = True
            self._account = AuthAccount(
                is_authenticated=True,
                username=getattr(info, "username", None) or self._username or None,
                full_name=getattr(info, "full_name", None) or "",
                profile_pic_url=str(info.profile_pic_url)
                if getattr(info, "profile_pic_url", None)
                else None,
            )
            emit_event(
                logger,
                logging.INFO,
                "gateway.instagrapi.session_resumed",
                "Resumed cached Instagram session",
                username=self._account.username,
            )
            return self._account
        except Exception as exc:
            emit_event(
                logger,
                logging.WARNING,
                "gateway.instagrapi.session_invalid",
                "Cached Instagram session is invalid or expired",
                error_type=type(exc).__name__,
            )
            self._authenticated = False
            self._account = None
            return AuthAccount(is_authenticated=False)

    def login(
        self,
        username: str,
        password: str,
        verification_code: str | None = None,
    ) -> AuthAccount:
        self._client = Client()
        self._client.delay_range = [1, 3]

        try:
            if self._session_path.exists():
                self._client.load_settings(self._session_path)
                emit_event(
                    logger,
                    logging.INFO,
                    "gateway.instagrapi.session_loaded",
                    "Loaded device settings from session file",
                )

            if verification_code:
                self._client.login(username, password, verification_code=verification_code)
            else:
                self._client.login(username, password)

            self._session_path.parent.mkdir(parents=True, exist_ok=True)
            self._client.dump_settings(self._session_path)

            info = self._client.account_info()
            self._username = username
            self._password = password
            self._authenticated = True
            self._account = AuthAccount(
                is_authenticated=True,
                username=getattr(info, "username", None) or username,
                full_name=getattr(info, "full_name", None) or "",
                profile_pic_url=str(info.profile_pic_url)
                if getattr(info, "profile_pic_url", None)
                else None,
            )
            emit_event(
                logger,
                logging.INFO,
                "gateway.instagrapi.authenticated",
                "Authenticated with Instagram",
                username=self._account.username,
            )
            return self._account
        except TwoFactorRequired as exc:
            emit_event(
                logger,
                logging.WARNING,
                "gateway.instagrapi.two_factor_required",
                "Instagram 2FA verification code required",
            )
            raise TwoFactorRequiredError(
                "Codigo de verificacao em duas etapas (2FA) necessario."
            ) from exc
        except ChallengeRequired as exc:
            emit_event(
                logger,
                logging.WARNING,
                "gateway.instagrapi.challenge_required",
                "Instagram security challenge required",
            )
            raise ChallengeRequiredError(
                "Instagram solicitou confirmacao de seguranca (Checkpoint). "
                "Aprove o login no app e tente novamente."
            ) from exc
        except LoginRequired as exc:
            raise GatewayAuthError(f"Credenciais ou sessao invalidas no Instagram: {exc}") from exc
        except PleaseWaitFewMinutes as exc:
            emit_event(
                logger,
                logging.WARNING,
                "gateway.instagrapi.rate_limited",
                "Instagram rate limit hit during login",
            )
            raise RateLimitError(f"Instagram rate limit hit during login: {exc}") from exc
        except Exception as exc:
            raise GatewayError(f"Failed to authenticate with Instagram: {exc}") from exc

    def logout(self) -> None:
        self._authenticated = False
        self._account = None
        self._username = ""
        self._password = ""
        self._client = Client()
        self._client.delay_range = [1, 3]
        if self._session_path.exists():
            self._session_path.unlink()

    def _ensure_authenticated(self) -> None:
        if self._authenticated:
            return
        status = self.get_auth_status()
        if status.is_authenticated:
            return
        if self._username and self._password:
            self.login(self._username, self._password)
            return
        raise GatewayAuthError("Sessao do Instagram nao autenticada. Faca login primeiro.")

    def fetch_following(self) -> list[GatewayProfile]:
        self._ensure_authenticated()
        try:
            user_id = self._client.user_id
            raw_users = self._client.user_following(user_id, amount=0)
            return [self._map_user(user) for user in raw_users.values()]
        except PleaseWaitFewMinutes as exc:
            raise RateLimitError(f"Instagram rate limit hit while fetching following: {exc}") from exc
        except Exception as exc:
            raise GatewayError(f"Error fetching following list: {exc}") from exc

    def fetch_followers(self) -> list[GatewayProfile]:
        self._ensure_authenticated()
        try:
            user_id = self._client.user_id
            raw_users = self._client.user_followers(user_id, amount=0)
            return [self._map_user(user) for user in raw_users.values()]
        except PleaseWaitFewMinutes as exc:
            raise RateLimitError(f"Instagram rate limit hit while fetching followers: {exc}") from exc
        except Exception as exc:
            raise GatewayError(f"Error fetching followers list: {exc}") from exc

    def unfollow(self, pk: str) -> None:
        self._ensure_authenticated()
        try:
            self._client.user_unfollow(int(pk))
        except PleaseWaitFewMinutes as exc:
            raise RateLimitError(f"Instagram rate limit hit while unfollowing {pk}: {exc}") from exc
        except Exception as exc:
            raise GatewayError(f"Error unfollowing user {pk}: {exc}") from exc

    @staticmethod
    def _map_user(user: Any) -> GatewayProfile:
        return GatewayProfile(
            pk=str(user.pk),
            username=user.username or "",
            full_name=user.full_name or "",
            profile_pic_url=str(user.profile_pic_url) if user.profile_pic_url else None,
            is_verified=bool(getattr(user, "is_verified", False)),
        )
