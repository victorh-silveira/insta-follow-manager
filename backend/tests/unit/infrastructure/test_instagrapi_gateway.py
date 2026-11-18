"""Unit tests for InstagrapiGateway using a fake instagrapi Client."""

from pathlib import Path
from types import SimpleNamespace

from instagrapi.exceptions import (
    ChallengeRequired,
    LoginRequired,
    PleaseWaitFewMinutes,
    TwoFactorRequired,
)
import pytest

from src.domain.exceptions import (
    ChallengeRequiredError,
    GatewayAuthError,
    GatewayError,
    RateLimitError,
    TwoFactorRequiredError,
)
from src.infrastructure.gateways import instagrapi_gateway as gw_module
from src.infrastructure.gateways.instagrapi_gateway import InstagrapiGateway


class _FakeClient:
    def __init__(self) -> None:
        self.user_id = 999
        self.sessionid = "sid-123"
        self.delay_range: list[int] = []
        self.loaded_path: Path | None = None
        self.dumped_path: Path | None = None
        self.unfollowed: list[int] = []
        self.removed_followers: list[str] = []
        self.login_error: Exception | None = None
        self.account_error: Exception | None = None
        self.following_error: Exception | None = None
        self.followers_error: Exception | None = None
        self.followers_gql_error: Exception | None = None
        self.unfollow_error: Exception | None = None
        self.remove_follower_error: Exception | None = None
        self.last_use_cache: bool | None = None
        self.last_verification_code: str | None = None
        self.challenge_code_handler: object | None = None
        self.trigger_challenge_handler: bool = False
        self.last_challenge_code_result: str | None = None

    def load_settings(self, path: Path) -> None:
        self.loaded_path = path

    def login_by_sessionid(self, sessionid: str) -> None:
        self.sessionid = sessionid

    def account_info(self) -> SimpleNamespace:
        if self.account_error:
            raise self.account_error
        return SimpleNamespace(
            username="victor.real",
            full_name="Victor Silveira",
            profile_pic_url="https://example.com/me.jpg",
        )

    def login(self, username: str, password: str, verification_code: str = "") -> None:
        self.last_verification_code = verification_code
        if self.trigger_challenge_handler and callable(self.challenge_code_handler):
            self.last_challenge_code_result = self.challenge_code_handler(username, "EMAIL")
        if self.login_error:
            raise self.login_error

    def dump_settings(self, path: Path) -> None:
        self.dumped_path = path
        path.write_text('{"session": true}', encoding="utf-8")

    def user_following(
        self, user_id: int, use_cache: bool = True, amount: int = 0
    ) -> dict[str, SimpleNamespace]:
        self.last_use_cache = use_cache
        if self.following_error:
            raise self.following_error
        return {
            "1": SimpleNamespace(
                pk=1,
                username="ana",
                full_name="Ana Julia",
                profile_pic_url="https://example.com/ana.jpg",
                is_verified=True,
            )
        }

    def user_followers_v1(self, user_id: int, amount: int = 0) -> list[SimpleNamespace]:
        if self.followers_error:
            raise self.followers_error
        return [
            SimpleNamespace(
                pk=2,
                username="bruno",
                full_name="Bruno Lima",
                profile_pic_url=None,
                is_verified=False,
            )
        ]

    def user_followers_private_gql(self, user_id: int, amount: int = 0) -> list[SimpleNamespace]:
        if self.followers_gql_error:
            raise self.followers_gql_error
        return [
            SimpleNamespace(
                pk=2,
                username="bruno",
                full_name="Bruno Lima",
                profile_pic_url=None,
                is_verified=False,
            ),
            SimpleNamespace(
                pk=3,
                username="lucasants02",
                full_name="Lucas Santos",
                profile_pic_url=None,
                is_verified=False,
            ),
        ]

    def user_unfollow(self, user_id: int) -> None:
        if self.unfollow_error:
            raise self.unfollow_error
        self.unfollowed.append(user_id)

    def user_remove_follower(self, user_id: str) -> bool:
        if self.remove_follower_error:
            raise self.remove_follower_error
        self.removed_followers.append(user_id)
        return True


def test_instagrapi_gateway_requires_login_when_no_session_or_credentials(tmp_path: Path) -> None:
    gateway = InstagrapiGateway(session_path=str(tmp_path / "missing.json"))
    assert gateway.get_auth_status().is_authenticated is False
    with pytest.raises(GatewayAuthError):
        gateway.fetch_following()


def test_instagrapi_gateway_resumes_cached_session_and_handles_invalid_session(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_client = _FakeClient()
    monkeypatch.setattr(gw_module, "Client", lambda: fake_client)

    session_file = tmp_path / "session.json"
    session_file.write_text("{}", encoding="utf-8")

    gateway = InstagrapiGateway(session_path=str(session_file))
    assert len(gateway.fetch_following()) == 1
    status = gateway.get_auth_status()
    assert status.is_authenticated is True
    assert status.username == "victor.real"
    assert gateway.get_auth_status().username == "victor.real"

    gateway.logout()
    assert not session_file.exists()

    session_file.write_text("{}", encoding="utf-8")
    fake_client.account_error = RuntimeError("expired")
    assert gateway.get_auth_status().is_authenticated is False


def test_instagrapi_gateway_loads_session_and_executes_operations(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_client = _FakeClient()
    monkeypatch.setattr(gw_module, "Client", lambda: fake_client)

    session_file = tmp_path / "session.json"
    session_file.write_text("{}", encoding="utf-8")

    gateway = InstagrapiGateway("user", "pass", str(session_file))
    assert gateway.mode_name == "instagrapi"

    gateway.login("user", "pass")
    assert fake_client.loaded_path == session_file
    assert fake_client.dumped_path == session_file

    following = gateway.fetch_following()
    assert len(following) == 1
    assert following[0].pk == "1"
    assert following[0].is_verified is True

    followers = gateway.fetch_followers()
    assert len(followers) == 2
    assert {f.pk for f in followers} == {"2", "3"}

    gateway.unfollow("102")
    assert fake_client.unfollowed == [102]


def test_instagrapi_gateway_login_with_2fa_code(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fake_client = _FakeClient()
    monkeypatch.setattr(gw_module, "Client", lambda: fake_client)

    gateway = InstagrapiGateway(session_path=str(tmp_path / "s.json"))
    account = gateway.login("user", "pass", verification_code="654321")
    assert account.is_authenticated is True
    assert fake_client.last_verification_code == "654321"


@pytest.mark.parametrize(
    ("exc_factory", "expected_exc"),
    [
        (lambda: TwoFactorRequired("2fa"), TwoFactorRequiredError),
        (lambda: ChallengeRequired("challenge"), ChallengeRequiredError),
        (lambda: LoginRequired("bad"), GatewayAuthError),
        (lambda: PleaseWaitFewMinutes("wait"), RateLimitError),
        (lambda: RuntimeError("boom"), GatewayError),
    ],
)
def test_instagrapi_gateway_maps_login_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    exc_factory: object,
    expected_exc: type[Exception],
) -> None:
    fake_client = _FakeClient()
    fake_client.login_error = exc_factory()  # type: ignore[operator]
    monkeypatch.setattr(gw_module, "Client", lambda: fake_client)

    gateway = InstagrapiGateway("user", "pass", str(tmp_path / "missing.json"))
    with pytest.raises(expected_exc):
        gateway.fetch_following()


@pytest.mark.parametrize(
    ("exc_factory", "expected_exc"),
    [
        (lambda: PleaseWaitFewMinutes("wait"), RateLimitError),
        (lambda: RuntimeError("boom"), GatewayError),
    ],
)
def test_instagrapi_gateway_maps_operation_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    exc_factory: object,
    expected_exc: type[Exception],
) -> None:
    fake_client = _FakeClient()
    monkeypatch.setattr(gw_module, "Client", lambda: fake_client)

    gateway = InstagrapiGateway("user", "pass", str(tmp_path / "session.json"))
    gateway.fetch_following()
    assert fake_client.last_use_cache is False

    followers = gateway.fetch_followers()
    assert {f.username for f in followers} == {"bruno", "lucasants02"}

    fake_client.following_error = exc_factory()  # type: ignore[operator]
    with pytest.raises(expected_exc):
        gateway.fetch_following()
    fake_client.following_error = None

    fake_client.followers_error = RuntimeError("v1 partial failure")
    partial_followers = gateway.fetch_followers()
    assert {f.username for f in partial_followers} == {"bruno", "lucasants02"}

    fake_client.followers_error = exc_factory()  # type: ignore[operator]
    fake_client.followers_gql_error = exc_factory()  # type: ignore[operator]
    with pytest.raises(expected_exc):
        gateway.fetch_followers()
    fake_client.followers_error = None
    fake_client.followers_gql_error = None

    fake_client.unfollow_error = exc_factory()  # type: ignore[operator]
    with pytest.raises(expected_exc):
        gateway.unfollow("10")
    fake_client.unfollow_error = None

    gateway.remove_follower("10")
    assert fake_client.removed_followers == ["10"]

    fake_client.remove_follower_error = exc_factory()  # type: ignore[operator]
    with pytest.raises(expected_exc):
        gateway.remove_follower("10")


def test_instagrapi_gateway_challenge_code_handler_and_session_id(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fake_client = _FakeClient()
    fake_client.trigger_challenge_handler = True
    monkeypatch.setattr(gw_module, "Client", lambda: fake_client)

    session_file = tmp_path / "challenge_session.json"
    gateway = InstagrapiGateway(session_path=str(session_file))

    with pytest.raises(ChallengeRequiredError):
        gateway.login("user", "pass")
    assert session_file.exists()

    account = gateway.login("user", "pass", challenge_code="654321")
    assert account.is_authenticated is True
    assert fake_client.last_challenge_code_result == "654321"

    session_account = gateway.login("", "", session_id="sid-cookie")
    assert session_account.is_authenticated is True
    assert fake_client.sessionid == "sid-cookie"
