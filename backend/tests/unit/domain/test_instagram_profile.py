"""Unit tests for InstagramProfile entity."""

import pytest

from src.domain.entities.instagram_profile import InstagramProfile
from src.domain.exceptions import NotFollowingError


def test_profile_bucket_uses_full_name_not_username() -> None:
    profile = InstagramProfile(
        pk="1",
        username="zzz_user",
        full_name="Ana Julia",
        is_following=True,
    )
    assert profile.bucket == "A"


def test_mark_unfollowed_updates_state() -> None:
    profile = InstagramProfile(
        pk="1",
        username="ana.j",
        full_name="Ana Julia",
        is_following=True,
        is_follower=False,
    )
    profile.mark_unfollowed()
    assert profile.is_following is False


def test_mark_unfollowed_when_not_following_raises_error() -> None:
    profile = InstagramProfile(
        pk="1",
        username="ana.j",
        full_name="Ana Julia",
        is_following=False,
    )
    with pytest.raises(NotFollowingError):
        profile.mark_unfollowed()
