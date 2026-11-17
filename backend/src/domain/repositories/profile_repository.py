"""Repository port (interface) for InstagramProfile persistence."""

from abc import ABC, abstractmethod
from enum import StrEnum

from src.domain.entities.instagram_profile import InstagramProfile


class RelationshipListType(StrEnum):
    """Supported relationship views for triage."""

    FOLLOWING = "following"
    FOLLOWERS = "followers"
    NON_FOLLOWERS = "non_followers"


class ProfileRepository(ABC):
    """Abstract repository defining persistence operations for profiles."""

    @abstractmethod
    def replace_all(self, profiles: list[InstagramProfile]) -> None:
        """Replace all cached profiles with a freshly synced snapshot."""

    @abstractmethod
    def find_by_filter(
        self,
        list_type: RelationshipListType,
        bucket: str | None = None,
        search: str | None = None,
    ) -> list[InstagramProfile]:
        """Return profiles matching list_type, optional bucket, and optional search."""

    @abstractmethod
    def get_bucket_counts(self, list_type: RelationshipListType) -> dict[str, int]:
        """Return profile counts per bucket (A-Z, 0-9, SPECIAL) for a list type."""

    @abstractmethod
    def get_by_pk(self, pk: str) -> InstagramProfile | None:
        """Find a single profile by its Instagram primary key."""

    @abstractmethod
    def save(self, profile: InstagramProfile) -> None:
        """Persist updates to an existing profile."""
