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
        self.login_error: Exception | None = None
        self.account_error: Exception | None = None
        self.following_error: Exception | None = None
        self.followers_error: Exception | None = None
        self.unfollow_error: Exception | None = None
        self.last_verification_code: str | None = None

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
        if self.login_error:
            raise self.login_error

    def dump_settings(self, path: Path) -> None:
        self.dumped_path = path
        path.write_text('{"session": true}', encoding="utf-8")

    def user_following(self, user_id: int, amount: int = 0) -> dict[str, SimpleNamespace]:
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

    def user_followers(self, user_id: int, amount: int = 0) -> dict[str, SimpleNamespace]:
        if self.followers_error:
            raise self.followers_error
        return {
            "2": SimpleNamespace(
                pk=2,
                username="bruno",
                full_name="Bruno Lima",
                profile_pic_url=None,
                is_verified=False,
            )
        }

    def user_unfollow(self, user_id: int) -> None:
        if self.unfollow_error:
            raise self.unfollow_error
        self.unfollowed.append(user_id)


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
    # Resumes session automatically inside _ensure_authenticated()
    assert len(gateway.fetch_following()) == 1
    status = gateway.get_auth_status()
    assert status.is_authenticated is True
    assert status.username == "victor.real"
    # Second call hits cached _account branch
    assert gateway.get_auth_status().username == "victor.real"

    # Logout clears session file
    gateway.logout()
    assert not session_file.exists()

    # Invalid session file falls back gracefully to unauthenticated
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

    # Explicit login with existing session_file loads device settings & dumps updated session
    gateway.login("user", "pass")
    assert fake_client.loaded_path == session_file
    assert fake_client.dumped_path == session_file

    following = gateway.fetch_following()
    assert len(following) == 1
    assert following[0].pk == "1"
    assert following[0].is_verified is True

    followers = gateway.fetch_followers()
    assert len(followers) == 1
    assert followers[0].pk == "2"

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

    fake_client.following_error = exc_factory()  # type: ignore[operator]
    with pytest.raises(expected_exc):
        gateway.fetch_following()
    fake_client.following_error = None

    fake_client.followers_error = exc_factory()  # type: ignore[operator]
    with pytest.raises(expected_exc):
        gateway.fetch_followers()
    fake_client.followers_error = None

    fake_client.unfollow_error = exc_factory()  # type: ignore[operator]
    with pytest.raises(expected_exc):
        gateway.unfollow("10")
