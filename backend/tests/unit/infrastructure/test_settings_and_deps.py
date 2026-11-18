"""Unit tests for Settings and dependency wiring."""

from pathlib import Path

import pytest

from src.infrastructure.config.settings import Settings
from src.infrastructure.gateways.instagrapi_gateway import InstagrapiGateway
from src.presentation.api import dependencies


def test_settings_sqlite_path_fallback() -> None:
    default_settings = Settings()
    assert default_settings.database_url == "sqlite:///./data/insta_manager.db"
    assert default_settings.ig_session_path == "./data/session.json"

    s = Settings(database_url="/tmp/custom.db")
    assert s.sqlite_path == "/tmp/custom.db"


def test_get_instagram_gateway_instagrapi_branch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    dependencies.get_instagram_gateway.cache_clear()
    custom_settings = Settings(
        instagram_gateway="instagrapi",
        ig_username="u",
        ig_password="p",
        ig_session_path=str(tmp_path / "s.json"),
    )
    monkeypatch.setattr(dependencies, "get_settings", lambda: custom_settings)
    gw = dependencies.get_instagram_gateway()
    assert isinstance(gw, InstagrapiGateway)
    assert dependencies.get_auth_status_use_case() is not None
    assert dependencies.get_login_use_case() is not None
    assert dependencies.get_logout_use_case() is not None
    dependencies.get_instagram_gateway.cache_clear()
