"""REST endpoints for syncing, listing, and unfollowing Instagram profiles."""

from dataclasses import asdict

from fastapi import APIRouter, Depends, Query

from src.application.use_cases.list_profiles_by_bucket import ListProfilesByBucketUseCase
from src.application.use_cases.remove_follower import RemoveFollowerUseCase
from src.application.use_cases.sync_relationships import SyncRelationshipsUseCase
from src.application.use_cases.unfollow_profile import UnfollowProfileUseCase
from src.domain.repositories.profile_repository import RelationshipListType
from src.presentation.api.dependencies import (
    get_list_profiles_use_case,
    get_remove_follower_use_case,
    get_sync_use_case,
    get_unfollow_use_case,
)
from src.presentation.api.schemas import (
    ListProfilesResponse,
    ProfileResponse,
    RemoveFollowerResponse,
    SyncResponse,
    UnfollowResponse,
)

router = APIRouter(prefix="/api/relationships", tags=["relationships"])


@router.post("/sync", response_model=SyncResponse)
def sync_relationships(
    use_case: SyncRelationshipsUseCase = Depends(get_sync_use_case),
) -> SyncResponse:
    """Sync following and followers from Instagram into local SQLite cache."""
    result = use_case.execute()
    return SyncResponse(**asdict(result))


@router.get("", response_model=ListProfilesResponse)
def list_relationships(
    list_type: RelationshipListType = Query(default=RelationshipListType.FOLLOWING),
    bucket: str | None = Query(default=None),
    q: str | None = Query(default=None),
    use_case: ListProfilesByBucketUseCase = Depends(get_list_profiles_use_case),
) -> ListProfilesResponse:
    """List profiles filtered by relationship type, display-name bucket, and search."""
    result = use_case.execute(list_type=list_type, bucket=bucket, search=q)
    return ListProfilesResponse(
        profiles=[ProfileResponse(**asdict(p)) for p in result.profiles],
        bucket_counts=result.bucket_counts,
        total_in_list=result.total_in_list,
    )


@router.post("/{pk}/unfollow", response_model=UnfollowResponse)
def unfollow_profile(
    pk: str,
    use_case: UnfollowProfileUseCase = Depends(get_unfollow_use_case),
) -> UnfollowResponse:
    """Unfollow an Instagram user by pk and update local cache."""
    result = use_case.execute(pk)
    return UnfollowResponse(**asdict(result))


@router.post("/{pk}/remove-follower", response_model=RemoveFollowerResponse)
def remove_follower(
    pk: str,
    use_case: RemoveFollowerUseCase = Depends(get_remove_follower_use_case),
) -> RemoveFollowerResponse:
    """Remove a follower from the authenticated account and update local cache."""
    result = use_case.execute(pk)
    return RemoveFollowerResponse(**asdict(result))
