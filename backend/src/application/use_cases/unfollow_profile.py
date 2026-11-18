"""Use case for unfollowing an Instagram profile."""

import logging

from src.application.dto.profile_dto import UnfollowResultDTO
from src.application.event_logger import emit_event
from src.domain.exceptions import NotFollowingError, ProfileNotFoundError
from src.domain.gateways.instagram_gateway import InstagramGateway
from src.domain.repositories.profile_repository import ProfileRepository

logger = logging.getLogger(__name__)


class UnfollowProfileUseCase:
    """Sends an unfollow request to Instagram and updates the local repository."""

    def __init__(self, gateway: InstagramGateway, repository: ProfileRepository) -> None:
        self._gateway = gateway
        self._repository = repository

    def execute(self, pk: str) -> UnfollowResultDTO:
        """Unfollow the user identified by pk on Instagram and persist state."""
        profile = self._repository.get_by_pk(pk)
        if profile is None:
            emit_event(
                logger,
                logging.WARNING,
                "relationships.unfollow.not_found",
                "Target profile not found for unfollow",
                pk=pk,
            )
            raise ProfileNotFoundError(f"Profile with pk={pk!r} was not found.")

        if not profile.is_following:
            emit_event(
                logger,
                logging.WARNING,
                "relationships.unfollow.not_following",
                "Target profile is not currently followed",
                pk=pk,
                username=profile.username,
            )
            raise NotFollowingError(f"Profile '{profile.username}' (pk={pk}) is not currently followed.")

        emit_event(
            logger,
            logging.INFO,
            "relationships.unfollow.requested",
            "Sending unfollow command to gateway",
            pk=pk,
            username=profile.username,
            bucket=profile.bucket,
            gateway_mode=self._gateway.mode_name,
        )

        self._gateway.unfollow(pk)
        profile.mark_unfollowed()

        follower_removed = False
        if profile.is_follower:
            self._gateway.remove_follower(pk)
            profile.mark_follower_removed()
            follower_removed = True
            emit_event(
                logger,
                logging.INFO,
                "relationships.unfollow.follower_also_removed",
                "Also removed unfollowed user from followers",
                pk=pk,
                username=profile.username,
            )

        self._repository.save(profile)

        emit_event(
            logger,
            logging.INFO,
            "relationships.unfollow.succeeded",
            "Profile unfollowed and cache updated",
            pk=pk,
            username=profile.username,
            bucket=profile.bucket,
            follower_removed=follower_removed,
        )

        return UnfollowResultDTO(
            pk=profile.pk,
            username=profile.username,
            full_name=profile.full_name,
            unfollowed=True,
            follower_removed=follower_removed,
        )
