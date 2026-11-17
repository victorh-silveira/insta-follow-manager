"""Integration tests for FastAPI relationships endpoints with SQLite."""

from pathlib import Path

from fastapi.testclient import TestClient
import pytest

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
