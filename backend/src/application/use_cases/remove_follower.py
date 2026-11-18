"""Use case for removing a follower from the authenticated Instagram account."""

import logging

from src.application.dto.profile_dto import RemoveFollowerResultDTO
from src.application.event_logger import emit_event
from src.domain.exceptions import NotFollowerError, ProfileNotFoundError
from src.domain.gateways.instagram_gateway import InstagramGateway
from src.domain.repositories.profile_repository import ProfileRepository

logger = logging.getLogger(__name__)


class RemoveFollowerUseCase:
    """Sends a remove-follower request to Instagram and updates the local repository."""

    def __init__(self, gateway: InstagramGateway, repository: ProfileRepository) -> None:
        self._gateway = gateway
        self._repository = repository

    def execute(self, pk: str) -> RemoveFollowerResultDTO:
        """Remove the follower identified by pk on Instagram and persist state."""
        profile = self._repository.get_by_pk(pk)
        if profile is None:
            emit_event(
                logger,
                logging.WARNING,
                "relationships.remove_follower.not_found",
                "Target profile not found for follower removal",
                pk=pk,
            )
            raise ProfileNotFoundError(f"Profile with pk={pk!r} was not found.")

        if not profile.is_follower:
            emit_event(
                logger,
                logging.WARNING,
                "relationships.remove_follower.not_follower",
                "Target profile is not currently a follower",
                pk=pk,
                username=profile.username,
            )
            raise NotFollowerError(
                f"Profile '{profile.username}' (pk={pk}) is not currently a follower."
            )

        emit_event(
            logger,
            logging.INFO,
            "relationships.remove_follower.requested",
            "Sending remove-follower command to gateway",
            pk=pk,
            username=profile.username,
            bucket=profile.bucket,
            gateway_mode=self._gateway.mode_name,
        )

        self._gateway.remove_follower(pk)
        profile.mark_follower_removed()
        self._repository.save(profile)

        emit_event(
            logger,
            logging.INFO,
            "relationships.remove_follower.succeeded",
            "Follower removed and cache updated",
            pk=pk,
            username=profile.username,
            bucket=profile.bucket,
        )

        return RemoveFollowerResultDTO(
            pk=profile.pk,
            username=profile.username,
            full_name=profile.full_name,
            removed=True,
        )
