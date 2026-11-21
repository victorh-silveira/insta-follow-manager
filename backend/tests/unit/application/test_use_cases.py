"""Unit tests for application use cases using in-memory test doubles."""

import pytest

from src.application.use_cases.auth_instagram import (
    GetAuthStatusUseCase,
    LoginInstagramUseCase,
    LogoutInstagramUseCase,
)
from src.application.use_cases.list_profiles_by_bucket import ListProfilesByBucketUseCase
from src.application.use_cases.remove_follower import RemoveFollowerUseCase
from src.application.use_cases.sync_relationships import SyncRelationshipsUseCase
from src.application.use_cases.unfollow_profile import UnfollowProfileUseCase
from src.domain.entities.instagram_profile import InstagramProfile
from src.domain.exceptions import (
    GatewayError,
    NotFollowerError,
    NotFollowingError,
    ProfileNotFoundError,
)
from src.domain.gateways.instagram_gateway import (
    AuthAccount,
    GatewayProfile,
    InstagramGateway,
)
from src.domain.repositories.profile_repository import (
    ProfileRepository,
    RelationshipListType,
)
from src.domain.value_objects.name_bucket import ALL_BUCKETS


class InMemoryProfileRepository(ProfileRepository):
    def __init__(self) -> None:
        self._store: dict[str, InstagramProfile] = {}

    def replace_all(self, profiles: list[InstagramProfile]) -> None:
        self._store = {p.pk: p for p in profiles}

    def _filter_by_list(self, list_type: RelationshipListType) -> list[InstagramProfile]:
        if list_type == RelationshipListType.FOLLOWING:
            return [p for p in self._store.values() if p.is_following]
        if list_type == RelationshipListType.FOLLOWERS:
            return [p for p in self._store.values() if p.is_follower]
        if list_type == RelationshipListType.NOT_FOLLOWING_BACK:
            return [p for p in self._store.values() if p.is_follower and not p.is_following]
        return [p for p in self._store.values() if p.is_following and not p.is_follower]

    def find_by_filter(
        self,
        list_type: RelationshipListType,
        bucket: str | None = None,
        search: str | None = None,
    ) -> list[InstagramProfile]:
        items = self._filter_by_list(list_type)
        if bucket:
            items = [p for p in items if p.bucket == bucket]
        if search:
            q = search.casefold()
            items = [p for p in items if q in p.full_name.casefold() or q in p.username.casefold()]
        return items

    def get_bucket_counts(self, list_type: RelationshipListType) -> dict[str, int]:
        counts = {bucket: 0 for bucket in ALL_BUCKETS}
        for profile in self._filter_by_list(list_type):
            counts[profile.bucket] += 1
        return counts

    def get_by_pk(self, pk: str) -> InstagramProfile | None:
        return self._store.get(pk)

    def save(self, profile: InstagramProfile) -> None:
        self._store[profile.pk] = profile


class FakeInstagramGateway(InstagramGateway):
    def __init__(self, should_fail_unfollow: bool = False) -> None:
        self.unfollowed_pks: list[str] = []
        self.removed_follower_pks: list[str] = []
        self.should_fail_unfollow = should_fail_unfollow
        self.authenticated = True

    @property
    def mode_name(self) -> str:
        return "fake"

    def get_auth_status(self) -> AuthAccount:
        return AuthAccount(is_authenticated=self.authenticated, username="fake_user")

    def login(
        self,
        username: str,
        password: str,
        verification_code: str | None = None,
        challenge_code: str | None = None,
        session_id: str | None = None,
    ) -> AuthAccount:
        self.authenticated = True
        self.last_challenge_code = challenge_code
        self.last_session_id = session_id
        return AuthAccount(is_authenticated=True, username=username or "session_user")

    def logout(self) -> None:
        self.authenticated = False

    def fetch_following(self) -> list[GatewayProfile]:
        return [
            GatewayProfile(pk="1", username="z_ana", full_name="Ana Julia"),
            GatewayProfile(pk="2", username="x_artur", full_name="Artur Lima"),
            GatewayProfile(pk="3", username="b_andre", full_name="André Costa"),
            GatewayProfile(pk="4", username="studio3d", full_name="3D Studio"),
            GatewayProfile(pk="5", username="lua_star", full_name="✨ Lua"),
        ]

    def fetch_followers(self) -> list[GatewayProfile]:
        return [
            GatewayProfile(pk="1", username="z_ana", full_name="Ana Julia"),
            GatewayProfile(pk="6", username="bruno_f", full_name="Bruno Ferreira"),
        ]

    def unfollow(self, pk: str) -> None:
        if self.should_fail_unfollow:
            raise GatewayError("Instagram unavailable")
        self.unfollowed_pks.append(pk)

    def remove_follower(self, pk: str) -> None:
        if self.should_fail_unfollow:
            raise GatewayError("Instagram unavailable")
        self.removed_follower_pks.append(pk)


def test_sync_merges_following_and_followers_accurately() -> None:
    repo = InMemoryProfileRepository()
    gateway = FakeInstagramGateway()

    result = SyncRelationshipsUseCase(gateway, repo).execute()

    assert result.total_profiles == 6
    assert result.following_count == 5
    assert result.followers_count == 2
    assert result.non_followers_count == 4
    assert result.gateway_mode == "fake"

    ana = repo.get_by_pk("1")
    assert ana is not None
    assert ana.is_following is True
    assert ana.is_follower is True


def test_list_profiles_by_bucket_filters_and_sorts_alphabetically() -> None:
    repo = InMemoryProfileRepository()
    gateway = FakeInstagramGateway()
    SyncRelationshipsUseCase(gateway, repo).execute()

    result = ListProfilesByBucketUseCase(repo).execute(
        list_type=RelationshipListType.FOLLOWING,
        bucket="A",
    )

    names = [p.full_name for p in result.profiles]
    assert names == ["Ana Julia", "André Costa", "Artur Lima"]
    assert result.bucket_counts["A"] == 3
    assert result.bucket_counts["0-9"] == 1
    assert result.bucket_counts["SPECIAL"] == 1
    assert result.total_in_list == 5


def test_unfollow_calls_gateway_and_updates_repository() -> None:
    repo = InMemoryProfileRepository()
    gateway = FakeInstagramGateway()
    SyncRelationshipsUseCase(gateway, repo).execute()

    result = UnfollowProfileUseCase(gateway, repo).execute("2")

    assert result.unfollowed is True
    assert gateway.unfollowed_pks == ["2"]
    artur = repo.get_by_pk("2")
    assert artur is not None
    assert artur.is_following is False


def test_unfollow_keeps_local_state_when_gateway_fails() -> None:
    repo = InMemoryProfileRepository()
    gateway = FakeInstagramGateway(should_fail_unfollow=True)
    SyncRelationshipsUseCase(gateway, repo).execute()

    with pytest.raises(GatewayError):
        UnfollowProfileUseCase(gateway, repo).execute("2")

    artur = repo.get_by_pk("2")
    assert artur is not None
    assert artur.is_following is True


def test_unfollow_unknown_pk_raises_not_found() -> None:
    repo = InMemoryProfileRepository()
    gateway = FakeInstagramGateway()

    with pytest.raises(ProfileNotFoundError):
        UnfollowProfileUseCase(gateway, repo).execute("999")


def test_unfollow_non_followed_profile_raises_error() -> None:
    repo = InMemoryProfileRepository()
    gateway = FakeInstagramGateway()
    SyncRelationshipsUseCase(gateway, repo).execute()

    with pytest.raises(NotFollowingError):
        UnfollowProfileUseCase(gateway, repo).execute("6")


def test_list_profiles_all_bucket_and_invalid_bucket() -> None:
    repo = InMemoryProfileRepository()
    gateway = FakeInstagramGateway()
    SyncRelationshipsUseCase(gateway, repo).execute()

    use_case = ListProfilesByBucketUseCase(repo)
    all_res = use_case.execute(list_type=RelationshipListType.FOLLOWING, bucket="ALL")
    assert len(all_res.profiles) == 5

    with pytest.raises(ValueError, match="Unsupported bucket filter"):
        use_case.execute(list_type=RelationshipListType.FOLLOWING, bucket="INVALID")


def test_auth_use_cases_lifecycle() -> None:
    gateway = FakeInstagramGateway()
    status = GetAuthStatusUseCase(gateway).execute()
    assert status.authenticated is True

    logged_out = LogoutInstagramUseCase(gateway).execute()
    assert logged_out.authenticated is False

    logged_in = LoginInstagramUseCase(gateway).execute("@victor.dev", "secret")
    assert logged_in.authenticated is True
    assert logged_in.username == "victor.dev"

    with pytest.raises(ValueError):
        LoginInstagramUseCase(gateway).execute("   ", "")


def test_remove_follower_calls_gateway_and_updates_repository() -> None:
    repo = InMemoryProfileRepository()
    gateway = FakeInstagramGateway()
    SyncRelationshipsUseCase(gateway, repo).execute()

    result = RemoveFollowerUseCase(gateway, repo).execute("6")

    assert result.removed is True
    assert gateway.removed_follower_pks == ["6"]
    bruno = repo.get_by_pk("6")
    assert bruno is not None
    assert bruno.is_follower is False


def test_remove_follower_errors_for_missing_or_non_follower() -> None:
    repo = InMemoryProfileRepository()
    gateway = FakeInstagramGateway()
    SyncRelationshipsUseCase(gateway, repo).execute()

    with pytest.raises(ProfileNotFoundError):
        RemoveFollowerUseCase(gateway, repo).execute("missing")

    with pytest.raises(NotFollowerError):
        RemoveFollowerUseCase(gateway, repo).execute("2")


def test_unfollow_mutual_profile_also_removes_follower() -> None:
    repo = InMemoryProfileRepository()
    gateway = FakeInstagramGateway()
    SyncRelationshipsUseCase(gateway, repo).execute()

    result = UnfollowProfileUseCase(gateway, repo).execute("1")

    assert result.unfollowed is True
    assert result.follower_removed is True
    assert gateway.unfollowed_pks == ["1"]
    assert gateway.removed_follower_pks == ["1"]

    ana = repo.get_by_pk("1")
    assert ana is not None
    assert ana.is_following is False
    assert ana.is_follower is False


def test_list_not_following_back_returns_followers_not_followed_back() -> None:
    repo = InMemoryProfileRepository()
    gateway = FakeInstagramGateway()
    SyncRelationshipsUseCase(gateway, repo).execute()

    result = ListProfilesByBucketUseCase(repo).execute(
        list_type=RelationshipListType.NOT_FOLLOWING_BACK,
        bucket="ALL",
    )

    assert [p.pk for p in result.profiles] == ["6"]


def test_login_instagram_use_case_with_session_id() -> None:
    gateway = FakeInstagramGateway()
    from src.application.use_cases.auth_instagram import LoginInstagramUseCase

    account = LoginInstagramUseCase(gateway).execute(
        username="",
        password="",
        session_id="sid-xyz",
    )

    assert account.authenticated is True
    assert account.username == "session_user"
    assert gateway.last_session_id == "sid-xyz"


def test_get_relationship_analytics_computes_kpis_and_top_buckets() -> None:
    repo = InMemoryProfileRepository()
    gateway = FakeInstagramGateway()
    SyncRelationshipsUseCase(gateway, repo).execute()

    from src.application.use_cases.get_relationship_analytics import GetRelationshipAnalyticsUseCase

    analytics = GetRelationshipAnalyticsUseCase(repo).execute()

    assert analytics.total_cached == 6
    assert analytics.following_count == 5
    assert analytics.followers_count == 2
    assert analytics.mutual_count == 1
    assert analytics.non_followers_count == 4
    assert analytics.not_following_back_count == 1
    assert analytics.follow_back_rate == 20.0
    assert analytics.follower_following_ratio == 0.4
    assert len(analytics.top_buckets) >= 1
