"""Dependency injection container for FastAPI routes."""

from functools import lru_cache

from src.application.use_cases.list_profiles_by_bucket import ListProfilesByBucketUseCase
from src.application.use_cases.sync_relationships import SyncRelationshipsUseCase
from src.application.use_cases.unfollow_profile import UnfollowProfileUseCase
from src.domain.gateways.instagram_gateway import InstagramGateway
from src.domain.repositories.profile_repository import ProfileRepository
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.gateways.instagrapi_gateway import InstagrapiGateway
from src.infrastructure.gateways.mock_instagram_gateway import MockInstagramGateway
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.persistence.sqlite_profile_repository import SQLiteProfileRepository


@lru_cache
def get_database() -> SQLiteDatabase:
    """Provide cached SQLiteDatabase instance."""
    settings: Settings = get_settings()
    return SQLiteDatabase(settings.sqlite_path)


@lru_cache
def get_profile_repository() -> ProfileRepository:
    """Provide ProfileRepository backed by SQLite."""
    return SQLiteProfileRepository(get_database())


@lru_cache
def get_instagram_gateway() -> InstagramGateway:
    """Provide configured InstagramGateway adapter (mock or instagrapi)."""
    settings: Settings = get_settings()
    if settings.instagram_gateway == "instagrapi":
        return InstagrapiGateway(
            username=settings.ig_username,
            password=settings.ig_password,
            session_path=settings.ig_session_path,
        )
    return MockInstagramGateway()


def get_sync_use_case() -> SyncRelationshipsUseCase:
    return SyncRelationshipsUseCase(get_instagram_gateway(), get_profile_repository())


def get_list_profiles_use_case() -> ListProfilesByBucketUseCase:
    return ListProfilesByBucketUseCase(get_profile_repository())


def get_unfollow_use_case() -> UnfollowProfileUseCase:
    return UnfollowProfileUseCase(get_instagram_gateway(), get_profile_repository())
