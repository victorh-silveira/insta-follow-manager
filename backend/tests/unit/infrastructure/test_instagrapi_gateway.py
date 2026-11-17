"""Unit tests for InstagrapiGateway using a fake instagrapi Client."""

from pathlib import Path
from types import SimpleNamespace

from instagrapi.exceptions import PleaseWaitFewMinutes, TwoFactorRequired
import pytest

from src.domain.exceptions import GatewayAuthError, GatewayError, RateLimitError
from src.infrastructure.gateways import instagrapi_gateway as gw_module
from src.infrastructure.gateways.instagrapi_gateway import InstagrapiGateway


class _FakeClient:
    def __init__(self) -> None:
        self.user_id = 999
        self.delay_range: list[int] = []
        self.loaded_path: Path | None = None
        self.dumped_path: Path | None = None
        self.unfollowed: list[int] = []
        self.login_error: Exception | None = None
        self.following_error: Exception | None = None
        self.followers_error: Exception | None = None
        self.unfollow_error: Exception | None = None

    def load_settings(self, path: Path) -> None:
        self.loaded_path = path

    def login(self, username: str, password: str) -> None:
        if self.login_error:
            raise self.login_error

    def dump_settings(self, path: Path) -> None:
        self.dumped_path = path

    def user_following(self, user_id: int) -> dict[str, SimpleNamespace]:
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

    def user_followers(self, user_id: int) -> dict[str, SimpleNamespace]:
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


def test_instagrapi_gateway_requires_credentials() -> None:
    with pytest.raises(GatewayAuthError):
        InstagrapiGateway(username="", password="", session_path="./session.json")


def test_instagrapi_gateway_loads_session_and_executes_operations(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_client = _FakeClient()
    monkeypatch.setattr(gw_module, "Client", lambda: fake_client)

    session_file = tmp_path / "session.json"
    session_file.write_text("{}", encoding="utf-8")

    gateway = InstagrapiGateway("user", "pass", str(session_file))
    assert gateway.mode_name == "instagrapi"

    following = gateway.fetch_following()
    assert len(following) == 1
    assert following[0].pk == "1"
    assert following[0].is_verified is True
    assert fake_client.loaded_path == session_file
    assert fake_client.dumped_path == session_file

    followers = gateway.fetch_followers()
    assert len(followers) == 1
    assert followers[0].pk == "2"

    gateway.unfollow("102")
    assert fake_client.unfollowed == [102]


@pytest.mark.parametrize(
    ("exc_factory", "expected_exc"),
    [
        (lambda: TwoFactorRequired("2fa"), GatewayAuthError),
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
