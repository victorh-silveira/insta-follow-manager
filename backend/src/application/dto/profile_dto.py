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
    follower_removed: bool = False


@dataclass(frozen=True)
class RemoveFollowerResultDTO:
    """Outcome of a remove-follower operation."""

    pk: str
    username: str
    full_name: str
    removed: bool


@dataclass(frozen=True)
class AuthStatusDTO:
    """Authentication status of the active Instagram session."""

    authenticated: bool
    gateway_mode: str
    username: str | None = None
    full_name: str | None = None
    profile_pic_url: str | None = None
    biography: str | None = None
    media_count: int | None = None
    follower_count: int | None = None
    following_count: int | None = None
    is_private: bool | None = None
    is_verified: bool = False


@dataclass(frozen=True)
class BucketCountDTO:
    """Count of profiles grouped by a single alphabetical bucket."""

    bucket: str
    count: int


@dataclass(frozen=True)
class RelationshipAnalyticsDTO:
    """Aggregated analytics computed from cached relationship profiles."""

    total_cached: int
    following_count: int
    followers_count: int
    mutual_count: int
    non_followers_count: int
    not_following_back_count: int
    follow_back_rate: float
    follower_following_ratio: float
    verified_following_count: int
    verified_followers_count: int
    nameless_profiles_count: int
    top_buckets: list[BucketCountDTO]
