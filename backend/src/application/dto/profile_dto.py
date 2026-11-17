"""Application-layer Data Transfer Objects."""

from dataclasses import dataclass

from src.domain.entities.instagram_profile import InstagramProfile


@dataclass(frozen=True)
class ProfileDTO:
    """Read-model representation of an Instagram profile for the presentation layer."""

    pk: str
    username: str
    full_name: str
    bucket: str
    profile_pic_url: str | None
    is_following: bool
    is_follower: bool
    is_verified: bool

    @classmethod
    def from_entity(cls, entity: InstagramProfile) -> "ProfileDTO":
        """Map a domain entity to a ProfileDTO."""
        return cls(
            pk=entity.pk,
            username=entity.username,
            full_name=entity.full_name,
            bucket=entity.bucket,
            profile_pic_url=entity.profile_pic_url,
            is_following=entity.is_following,
            is_follower=entity.is_follower,
            is_verified=entity.is_verified,
        )


@dataclass(frozen=True)
class SyncResultDTO:
    """Summary returned after syncing relationships from Instagram."""

    total_profiles: int
    following_count: int
    followers_count: int
    non_followers_count: int
    gateway_mode: str


@dataclass(frozen=True)
class ListProfilesResultDTO:
    """Paginated/filtered list of profiles along with A-Z/0-9/SPECIAL bucket counts."""

    profiles: list[ProfileDTO]
    bucket_counts: dict[str, int]
    total_in_list: int


@dataclass(frozen=True)
class UnfollowResultDTO:
    """Outcome of an unfollow operation."""

    pk: str
    username: str
    full_name: str
    unfollowed: bool
