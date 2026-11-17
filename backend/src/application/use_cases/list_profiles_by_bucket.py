"""Use case for listing profiles filtered by relationship type and alphabetical bucket."""

import logging

from src.application.dto.profile_dto import ListProfilesResultDTO, ProfileDTO
from src.application.event_logger import emit_event
from src.domain.repositories.profile_repository import (
    ProfileRepository,
    RelationshipListType,
)
from src.domain.value_objects.name_bucket import ALL_BUCKETS

logger = logging.getLogger(__name__)


class ListProfilesByBucketUseCase:
    """Returns alphabetically sorted profiles and bucket counts for triage UI."""

    def __init__(self, repository: ProfileRepository) -> None:
        self._repository = repository

    def execute(
        self,
        list_type: RelationshipListType,
        bucket: str | None = None,
        search: str | None = None,
    ) -> ListProfilesResultDTO:
        """Filter and sort profiles by display name bucket and optional search query."""
        normalized_bucket = self._normalize_bucket(bucket)
        cleaned_search = search.strip() if search else None
        profiles = self._repository.find_by_filter(
            list_type=list_type,
            bucket=normalized_bucket,
            search=cleaned_search,
        )
        profiles.sort(key=lambda profile: profile.sort_key)

        bucket_counts = self._repository.get_bucket_counts(list_type)
        total_in_list = sum(bucket_counts.values())

        emit_event(
            logger,
            logging.DEBUG,
            "relationships.list.queried",
            "Queried profiles by bucket",
            list_type=list_type.value,
            bucket=normalized_bucket or "ALL",
            has_search=bool(cleaned_search),
            returned_count=len(profiles),
            total_in_list=total_in_list,
        )

        return ListProfilesResultDTO(
            profiles=[ProfileDTO.from_entity(p) for p in profiles],
            bucket_counts=bucket_counts,
            total_in_list=total_in_list,
        )

    @staticmethod
    def _normalize_bucket(bucket: str | None) -> str | None:
        if not bucket or bucket.upper() == "ALL":
            return None
        candidate = bucket.upper()
        if candidate not in ALL_BUCKETS:
            raise ValueError(f"Unsupported bucket filter: {bucket!r}")
        return candidate
