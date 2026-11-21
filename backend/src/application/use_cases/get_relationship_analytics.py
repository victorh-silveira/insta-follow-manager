"""Use case for computing relationship analytics from cached profiles."""

from collections import Counter

from src.application.dto.profile_dto import BucketCountDTO, RelationshipAnalyticsDTO
from src.domain.repositories.profile_repository import ProfileRepository, RelationshipListType


class GetRelationshipAnalyticsUseCase:
    """Computes aggregated relationship and distribution metrics from cached profiles."""

    def __init__(self, repository: ProfileRepository) -> None:
        self._repository = repository

    def execute(self) -> RelationshipAnalyticsDTO:
        """Compute relationship KPIs, reciprocity rate, verified counts, and top buckets."""
        following = self._repository.find_by_filter(RelationshipListType.FOLLOWING)
        followers = self._repository.find_by_filter(RelationshipListType.FOLLOWERS)

        following_by_pk = {p.pk: p for p in following}
        followers_by_pk = {p.pk: p for p in followers}
        all_profiles = {**following_by_pk, **followers_by_pk}

        following_count = len(following)
        followers_count = len(followers)
        mutual_count = sum(1 for pk in following_by_pk if pk in followers_by_pk)
        non_followers_count = following_count - mutual_count
        not_following_back_count = followers_count - mutual_count

        follow_back_rate = (
            round((mutual_count / following_count) * 100, 1) if following_count > 0 else 0.0
        )
        follower_following_ratio = (
            round(followers_count / following_count, 2) if following_count > 0 else 0.0
        )

        verified_following_count = sum(1 for p in following if p.is_verified)
        verified_followers_count = sum(1 for p in followers if p.is_verified)
        nameless_profiles_count = sum(1 for p in all_profiles.values() if not p.full_name.strip())

        bucket_counter = Counter(p.bucket for p in all_profiles.values())
        top_buckets = [
            BucketCountDTO(bucket=bucket, count=count) for bucket, count in bucket_counter.most_common(8)
        ]

        return RelationshipAnalyticsDTO(
            total_cached=len(all_profiles),
            following_count=following_count,
            followers_count=followers_count,
            mutual_count=mutual_count,
            non_followers_count=non_followers_count,
            not_following_back_count=not_following_back_count,
            follow_back_rate=follow_back_rate,
            follower_following_ratio=follower_following_ratio,
            verified_following_count=verified_following_count,
            verified_followers_count=verified_followers_count,
            nameless_profiles_count=nameless_profiles_count,
            top_buckets=top_buckets,
        )
