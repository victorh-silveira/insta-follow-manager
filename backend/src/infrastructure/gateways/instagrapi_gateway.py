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
from src.domain.exceptions import GatewayAuthError, GatewayError, RateLimitError
from src.domain.gateways.instagram_gateway import GatewayProfile, InstagramGateway

logger = logging.getLogger(__name__)


class InstagrapiGateway(InstagramGateway):
    """Communicates with Instagram Private API via instagrapi with session caching."""

    def __init__(self, username: str, password: str, session_path: str) -> None:
        if not username or not password:
            raise GatewayAuthError(
                "IG_USERNAME and IG_PASSWORD must be configured when INSTAGRAM_GATEWAY=instagrapi."
            )
        self._username = username
        self._password = password
        self._session_path = Path(session_path)
        self._client = Client()
        self._client.delay_range = [1, 3]
        self._authenticated = False

    @property
    def mode_name(self) -> str:
        return "instagrapi"

    def _ensure_authenticated(self) -> None:
        if self._authenticated:
            return
        try:
            if self._session_path.exists():
                self._client.load_settings(self._session_path)
                emit_event(
                    logger,
                    logging.INFO,
                    "gateway.instagrapi.session_loaded",
                    "Loaded cached Instagram session file",
                )
            self._client.login(self._username, self._password)
            self._client.dump_settings(self._session_path)
            self._authenticated = True
            emit_event(
                logger,
                logging.INFO,
                "gateway.instagrapi.authenticated",
                "Authenticated with Instagram",
                username=self._username,
            )
        except (TwoFactorRequired, ChallengeRequired, LoginRequired) as exc:
            emit_event(
                logger,
                logging.WARNING,
                "gateway.instagrapi.auth_challenge",
                "Instagram authentication challenge required",
                error_type=type(exc).__name__,
            )
            raise GatewayAuthError(f"Instagram authentication challenge/login required: {exc}") from exc
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

    def fetch_following(self) -> list[GatewayProfile]:
        self._ensure_authenticated()
        try:
            user_id = self._client.user_id
            raw_users = self._client.user_following(user_id)
            return [self._map_user(user) for user in raw_users.values()]
        except PleaseWaitFewMinutes as exc:
            raise RateLimitError(f"Instagram rate limit hit while fetching following: {exc}") from exc
        except Exception as exc:
            raise GatewayError(f"Error fetching following list: {exc}") from exc

    def fetch_followers(self) -> list[GatewayProfile]:
        self._ensure_authenticated()
        try:
            user_id = self._client.user_id
            raw_users = self._client.user_followers(user_id)
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
