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


class RemoveFollowerResponse(BaseModel):
    """Response payload after a remove-follower action."""

    pk: str
    username: str
    full_name: str
    removed: bool


class LoginRequest(BaseModel):
    """Credentials payload sent from the frontend login form."""

    username: str
    password: str
    verification_code: str | None = None


class AuthStatusResponse(BaseModel):
    """Authenticated Instagram session status."""

    authenticated: bool
    gateway_mode: str
    username: str | None = None
    full_name: str | None = None
    profile_pic_url: str | None = None
