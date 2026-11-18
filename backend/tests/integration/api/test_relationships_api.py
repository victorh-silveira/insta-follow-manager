"""Integration tests for FastAPI relationships endpoints with SQLite."""

from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from src.application.use_cases.auth_instagram import (
    GetAuthStatusUseCase,
    LoginInstagramUseCase,
    LogoutInstagramUseCase,
)
from src.application.use_cases.sync_relationships import SyncRelationshipsUseCase
from src.domain.exceptions import (
    ChallengeRequiredError,
    GatewayAuthError,
    GatewayError,
    RateLimitError,
    TwoFactorRequiredError,
)
from src.infrastructure.gateways.mock_instagram_gateway import MockInstagramGateway
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.persistence.sqlite_profile_repository import SQLiteProfileRepository
from src.presentation.api import dependencies
from src.presentation.main import create_app


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    db_file = tmp_path / "test_insta.db"
    db = SQLiteDatabase(str(db_file))
    repo = SQLiteProfileRepository(db)
    gateway = MockInstagramGateway()

    app = create_app()
    app.dependency_overrides[dependencies.get_profile_repository] = lambda: repo
    app.dependency_overrides[dependencies.get_instagram_gateway] = lambda: gateway
    return TestClient(app)


def test_health_endpoint_returns_mock_mode(client: TestClient) -> None:
    response = client.get("/api/health", headers={"X-Request-ID": "trace-health-01"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "trace-health-01"
    assert response.json() == {"status": "ok", "gateway_mode": "mock"}


def test_api_generates_request_id_when_header_missing(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


def test_sync_and_filter_bucket_a_returns_sorted_display_names(client: TestClient) -> None:
    sync_resp = client.post("/api/relationships/sync")
    assert sync_resp.status_code == 200
    assert sync_resp.json()["following_count"] == 26

    resp = client.get("/api/relationships", params={"list_type": "following", "bucket": "A"})
    assert resp.status_code == 200
    payload = resp.json()

    names = [p["full_name"] for p in payload["profiles"]]
    assert names == ["Ágata Lima", "Ana Julia", "André Oliveira", "Artur Mendes"]
    assert payload["bucket_counts"]["A"] == 4
    assert payload["bucket_counts"]["0-9"] == 2
    assert payload["bucket_counts"]["SPECIAL"] == 3


def test_filter_digits_and_special_buckets(client: TestClient) -> None:
    client.post("/api/relationships/sync")

    digits_resp = client.get("/api/relationships", params={"list_type": "following", "bucket": "0-9"})
    assert digits_resp.status_code == 200
    assert [p["full_name"] for p in digits_resp.json()["profiles"]] == [
        "007 Tech News",
        "3D Studio Brasil",
    ]

    special_resp = client.get(
        "/api/relationships", params={"list_type": "following", "bucket": "SPECIAL"}
    )
    assert special_resp.status_code == 200
    assert len(special_resp.json()["profiles"]) == 3


def test_unfollow_endpoint_updates_following_list_and_counts(client: TestClient) -> None:
    client.post("/api/relationships/sync")

    unfollow_resp = client.post("/api/relationships/102/unfollow")
    assert unfollow_resp.status_code == 200
    assert unfollow_resp.json()["unfollowed"] is True

    after_resp = client.get("/api/relationships", params={"list_type": "following", "bucket": "A"})
    assert after_resp.status_code == 200
    names = [p["full_name"] for p in after_resp.json()["profiles"]]
    assert "Artur Mendes" not in names
    assert after_resp.json()["bucket_counts"]["A"] == 3


def test_unfollow_missing_profile_returns_404(client: TestClient) -> None:
    client.post("/api/relationships/sync")
    resp = client.post("/api/relationships/does-not-exist/unfollow")
    assert resp.status_code == 404


def test_unfollow_non_followed_profile_returns_400(client: TestClient) -> None:
    client.post("/api/relationships/sync")
    resp = client.post("/api/relationships/201/unfollow")
    assert resp.status_code == 400


def test_invalid_bucket_returns_422(client: TestClient) -> None:
    resp = client.get("/api/relationships", params={"list_type": "following", "bucket": "BAD"})
    assert resp.status_code == 422


@pytest.mark.parametrize(
    ("exc", "expected_status"),
    [
        (GatewayAuthError("auth"), 401),
        (RateLimitError("rate"), 429),
        (GatewayError("bad gateway"), 502),
    ],
)
def test_gateway_errors_map_to_http_status(tmp_path: Path, exc: Exception, expected_status: int) -> None:
    class FailingGateway(MockInstagramGateway):
        def fetch_following(self):  # type: ignore[override]
            raise exc

    db = SQLiteDatabase(str(tmp_path / "err.db"))
    app = create_app()
    repo = SQLiteProfileRepository(db)
    app.dependency_overrides[dependencies.get_sync_use_case] = lambda: SyncRelationshipsUseCase(
        FailingGateway(), repo
    )
    tc = TestClient(app)

    resp = tc.post("/api/relationships/sync")
    assert resp.status_code == expected_status


def test_unhandled_exception_logged_by_middleware(tmp_path: Path) -> None:
    class CrashGateway(MockInstagramGateway):
        def fetch_following(self):  # type: ignore[override]
            raise RuntimeError("unexpected crash")

    db = SQLiteDatabase(str(tmp_path / "crash.db"))
    app = create_app()
    repo = SQLiteProfileRepository(db)
    app.dependency_overrides[dependencies.get_sync_use_case] = lambda: SyncRelationshipsUseCase(
        CrashGateway(), repo
    )
    tc = TestClient(app, raise_server_exceptions=False)

    resp = tc.post("/api/relationships/sync")
    assert resp.status_code == 500


def test_auth_endpoints_status_login_logout(tmp_path: Path) -> None:
    gateway = MockInstagramGateway()
    app = create_app()
    app.dependency_overrides[dependencies.get_auth_status_use_case] = lambda: GetAuthStatusUseCase(
        gateway
    )
    app.dependency_overrides[dependencies.get_login_use_case] = lambda: LoginInstagramUseCase(gateway)
    app.dependency_overrides[dependencies.get_logout_use_case] = lambda: LogoutInstagramUseCase(gateway)
    tc = TestClient(app)

    status_resp = tc.get("/api/auth/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["authenticated"] is True

    logout_resp = tc.post("/api/auth/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json()["authenticated"] is False

    assert tc.get("/api/auth/status").json()["authenticated"] is False

    login_resp = tc.post(
        "/api/auth/login",
        json={"username": "victor.insta", "password": "secret"},
    )
    assert login_resp.status_code == 200
    assert login_resp.json()["authenticated"] is True
    assert login_resp.json()["username"] == "victor.insta"


@pytest.mark.parametrize(
    ("exc", "expected_flag"),
    [
        (TwoFactorRequiredError("2fa needed"), "requires_2fa"),
        (ChallengeRequiredError("checkpoint"), "requires_challenge"),
    ],
)
def test_auth_login_2fa_and_challenge_responses(exc: Exception, expected_flag: str) -> None:
    class AuthErrorGateway(MockInstagramGateway):
        def login(self, username: str, password: str, verification_code: str | None = None):  # type: ignore[override]
            raise exc

    app = create_app()
    app.dependency_overrides[dependencies.get_login_use_case] = lambda: LoginInstagramUseCase(
        AuthErrorGateway()
    )
    tc = TestClient(app)

    resp = tc.post("/api/auth/login", json={"username": "u", "password": "p"})
    assert resp.status_code == 401
    assert resp.json()[expected_flag] is True


def test_remove_follower_endpoint_updates_followers_and_handles_errors(
    client: TestClient,
) -> None:
    client.post("/api/relationships/sync")

    followers_resp = client.get("/api/relationships?list_type=followers&bucket=ALL")
    assert followers_resp.status_code == 200
    target = followers_resp.json()["profiles"][0]

    remove_resp = client.post(f"/api/relationships/{target['pk']}/remove-follower")
    assert remove_resp.status_code == 200
    assert remove_resp.json()["removed"] is True
    assert remove_resp.json()["pk"] == target["pk"]

    repeat_resp = client.post(f"/api/relationships/{target['pk']}/remove-follower")
    assert repeat_resp.status_code == 400

    missing_resp = client.post("/api/relationships/nonexistent-pk/remove-follower")
    assert missing_resp.status_code == 404
