"""InstagramProfile domain entity."""

from dataclasses import dataclass

from src.domain.exceptions import NotFollowingError
from src.domain.value_objects.name_bucket import NameBucket, normalize_for_sort


@dataclass
class InstagramProfile:
    """Represents an Instagram user in the context of follower/following triage."""

    pk: str
    username: str
    full_name: str
    profile_pic_url: str | None = None
    is_following: bool = False
    is_follower: bool = False
    is_verified: bool = False

    @property
    def bucket(self) -> str:
        """Return the A-Z, 0-9, or SPECIAL bucket derived from full_name."""
        return NameBucket.from_display_name(self.full_name).value

    @property
    def sort_key(self) -> tuple[str, str]:
        """Sort alphabetically by normalized full_name, then username."""
        return (normalize_for_sort(self.full_name), self.username.casefold())

    def mark_unfollowed(self) -> None:
        """Transition state after a successful unfollow on Instagram."""
        if not self.is_following:
            raise NotFollowingError(
                f"Profile '{self.username}' (pk={self.pk}) is not in the following list."
            )
        self.is_following = False
