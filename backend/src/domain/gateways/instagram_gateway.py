"""Gateway port (interface) for communicating with Instagram."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class GatewayProfile:
    """Raw profile data returned by an Instagram gateway adapter."""

    pk: str
    username: str
    full_name: str
    profile_pic_url: str | None = None
    is_verified: bool = False


@dataclass(frozen=True)
class AuthAccount:
    """Authenticated Instagram account summary returned by a gateway adapter."""

    is_authenticated: bool
    username: str | None = None
    full_name: str | None = None
    profile_pic_url: str | None = None
    biography: str | None = None
    media_count: int | None = None
    follower_count: int | None = None
    following_count: int | None = None
    is_private: bool | None = None
    is_verified: bool = False


class InstagramGateway(ABC):
    """Port for authenticating, fetching relationship lists, and unfollowing."""

    @property
    @abstractmethod
    def mode_name(self) -> str:
        """Human-readable identifier of the active gateway (e.g. 'mock', 'instagrapi')."""

    @abstractmethod
    def get_auth_status(self) -> AuthAccount:
        """Check whether an active Instagram session is currently authenticated."""

    @abstractmethod
    def login(
        self,
        username: str,
        password: str,
        verification_code: str | None = None,
        challenge_code: str | None = None,
        session_id: str | None = None,
    ) -> AuthAccount:
        """Authenticate against Instagram and persist session state."""

    @abstractmethod
    def logout(self) -> None:
        """Invalidate and remove the active Instagram session."""

    @abstractmethod
    def fetch_following(self) -> list[GatewayProfile]:
        """Fetch all accounts the authenticated user is following."""

    @abstractmethod
    def fetch_followers(self) -> list[GatewayProfile]:
        """Fetch all accounts following the authenticated user."""

    @abstractmethod
    def unfollow(self, pk: str) -> None:
        """Send an unfollow command to Instagram for the given user pk."""

    @abstractmethod
    def remove_follower(self, pk: str) -> None:
        """Remove the given user pk from the authenticated user's followers."""
