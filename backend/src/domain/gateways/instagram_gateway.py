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


class InstagramGateway(ABC):
    """Port for fetching relationship lists and executing unfollow actions."""

    @property
    @abstractmethod
    def mode_name(self) -> str:
        """Human-readable identifier of the active gateway (e.g. 'mock', 'instagrapi')."""

    @abstractmethod
    def fetch_following(self) -> list[GatewayProfile]:
        """Fetch all accounts the authenticated user is following."""

    @abstractmethod
    def fetch_followers(self) -> list[GatewayProfile]:
        """Fetch all accounts following the authenticated user."""

    @abstractmethod
    def unfollow(self, pk: str) -> None:
        """Send an unfollow command to Instagram for the given user pk."""
