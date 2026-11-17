"""Use case for syncing following and followers lists from Instagram."""

import logging
import time

from src.application.dto.profile_dto import SyncResultDTO
from src.application.event_logger import emit_event
from src.domain.entities.instagram_profile import InstagramProfile
from src.domain.gateways.instagram_gateway import GatewayProfile, InstagramGateway
from src.domain.repositories.profile_repository import ProfileRepository

logger = logging.getLogger(__name__)


class SyncRelationshipsUseCase:
    """Synchronizes local cache with Instagram following and followers lists."""

    def __init__(self, gateway: InstagramGateway, repository: ProfileRepository) -> None:
        self._gateway = gateway
        self._repository = repository

    def execute(self) -> SyncResultDTO:
        """Fetch following & followers, merge by pk, and persist to repository."""
        start = time.perf_counter()
        emit_event(
            logger,
            logging.INFO,
            "relationships.sync.started",
            "Starting relationship sync",
            gateway_mode=self._gateway.mode_name,
        )

        following = self._gateway.fetch_following()
        followers = self._gateway.fetch_followers()

        merged: dict[str, InstagramProfile] = {}

        for item in following:
            merged[item.pk] = self._to_entity(item, is_following=True, is_follower=False)

        for item in followers:
            existing = merged.get(item.pk)
            if existing is not None:
                existing.is_follower = True
            else:
                merged[item.pk] = self._to_entity(item, is_following=False, is_follower=True)

        profiles = list(merged.values())
        self._repository.replace_all(profiles)

        non_followers_count = sum(1 for p in profiles if p.is_following and not p.is_follower)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        emit_event(
            logger,
            logging.INFO,
            "relationships.sync.completed",
            "Relationship sync completed",
            gateway_mode=self._gateway.mode_name,
            total_profiles=len(profiles),
            following_count=len(following),
            followers_count=len(followers),
            non_followers_count=non_followers_count,
            duration_ms=duration_ms,
        )

        return SyncResultDTO(
            total_profiles=len(profiles),
            following_count=len(following),
            followers_count=len(followers),
            non_followers_count=non_followers_count,
            gateway_mode=self._gateway.mode_name,
        )

    @staticmethod
    def _to_entity(item: GatewayProfile, *, is_following: bool, is_follower: bool) -> InstagramProfile:
        return InstagramProfile(
            pk=item.pk,
            username=item.username,
            full_name=item.full_name,
            profile_pic_url=item.profile_pic_url,
            is_following=is_following,
            is_follower=is_follower,
            is_verified=item.is_verified,
        )
