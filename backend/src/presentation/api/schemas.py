"""Pydantic response schemas for the REST API."""

from pydantic import BaseModel


class ProfileResponse(BaseModel):
    """Serialized Instagram profile returned to the frontend."""

    pk: str
    username: str
    full_name: str
    bucket: str
    profile_pic_url: str | None
    is_following: bool
    is_follower: bool
    is_verified: bool


class SyncResponse(BaseModel):
    """Response payload after syncing Instagram relationships."""

    total_profiles: int
    following_count: int
    followers_count: int
    non_followers_count: int
    gateway_mode: str


class ListProfilesResponse(BaseModel):
    """Response payload for filtered relationship listings."""

    profiles: list[ProfileResponse]
    bucket_counts: dict[str, int]
    total_in_list: int


class UnfollowResponse(BaseModel):
    """Response payload after an unfollow action."""

    pk: str
    username: str
    full_name: str
    unfollowed: bool
    follower_removed: bool = False


class RemoveFollowerResponse(BaseModel):
    """Response payload after a remove-follower action."""

    pk: str
    username: str
    full_name: str
    removed: bool


class LoginRequest(BaseModel):
    """Credentials payload sent from the frontend login form."""

    username: str = ""
    password: str = ""
    verification_code: str | None = None
    challenge_code: str | None = None
    session_id: str | None = None


class AuthStatusResponse(BaseModel):
    """Authenticated Instagram session status."""

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


class BucketCountResponse(BaseModel):
    """Serialized bucket distribution entry."""

    bucket: str
    count: int


class RelationshipAnalyticsResponse(BaseModel):
    """Aggregated analytics payload for the home dashboard."""

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
    top_buckets: list[BucketCountResponse]
