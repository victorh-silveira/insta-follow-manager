"""SQLite implementation of ProfileRepository."""

import sqlite3

from src.domain.entities.instagram_profile import InstagramProfile
from src.domain.repositories.profile_repository import (
    ProfileRepository,
    RelationshipListType,
)
from src.domain.value_objects.name_bucket import ALL_BUCKETS
from src.infrastructure.persistence.database import SQLiteDatabase

_FILTER_QUERIES: dict[RelationshipListType, str] = {
    RelationshipListType.FOLLOWING: (
        "SELECT * FROM profiles WHERE is_following = 1 "
        "AND (? IS NULL OR bucket = ?) "
        "AND (? IS NULL OR LOWER(full_name) LIKE ? OR LOWER(username) LIKE ?)"
    ),
    RelationshipListType.FOLLOWERS: (
        "SELECT * FROM profiles WHERE is_follower = 1 "
        "AND (? IS NULL OR bucket = ?) "
        "AND (? IS NULL OR LOWER(full_name) LIKE ? OR LOWER(username) LIKE ?)"
    ),
    RelationshipListType.NON_FOLLOWERS: (
        "SELECT * FROM profiles WHERE is_following = 1 AND is_follower = 0 "
        "AND (? IS NULL OR bucket = ?) "
        "AND (? IS NULL OR LOWER(full_name) LIKE ? OR LOWER(username) LIKE ?)"
    ),
    RelationshipListType.NOT_FOLLOWING_BACK: (
        "SELECT * FROM profiles WHERE is_following = 0 AND is_follower = 1 "
        "AND (? IS NULL OR bucket = ?) "
        "AND (? IS NULL OR LOWER(full_name) LIKE ? OR LOWER(username) LIKE ?)"
    ),
}

_COUNT_QUERIES: dict[RelationshipListType, str] = {
    RelationshipListType.FOLLOWING: (
        "SELECT bucket, COUNT(*) AS total FROM profiles WHERE is_following = 1 GROUP BY bucket"
    ),
    RelationshipListType.FOLLOWERS: (
        "SELECT bucket, COUNT(*) AS total FROM profiles WHERE is_follower = 1 GROUP BY bucket"
    ),
    RelationshipListType.NON_FOLLOWERS: (
        "SELECT bucket, COUNT(*) AS total FROM profiles "
        "WHERE is_following = 1 AND is_follower = 0 GROUP BY bucket"
    ),
    RelationshipListType.NOT_FOLLOWING_BACK: (
        "SELECT bucket, COUNT(*) AS total FROM profiles "
        "WHERE is_following = 0 AND is_follower = 1 GROUP BY bucket"
    ),
}


class SQLiteProfileRepository(ProfileRepository):
    """Persists and queries cached Instagram profiles in SQLite."""

    def __init__(self, db: SQLiteDatabase) -> None:
        self._db = db

    def replace_all(self, profiles: list[InstagramProfile]) -> None:
        rows = [
            (
                p.pk,
                p.username,
                p.full_name,
                p.bucket,
                p.profile_pic_url,
                int(p.is_following),
                int(p.is_follower),
                int(p.is_verified),
            )
            for p in profiles
        ]
        with self._db.connection() as conn:
            conn.execute("DELETE FROM profiles")
            conn.executemany(
                """
                INSERT INTO profiles (
                    pk, username, full_name, bucket,
                    profile_pic_url, is_following, is_follower, is_verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

    def find_by_filter(
        self,
        list_type: RelationshipListType,
        bucket: str | None = None,
        search: str | None = None,
    ) -> list[InstagramProfile]:
        query = _FILTER_QUERIES[list_type]
        pattern = f"%{search.casefold()}%" if search else None
        params = (bucket, bucket, pattern, pattern, pattern)

        with self._db.connection() as conn:
            rows = conn.execute(query, params).fetchall()

        return [self._row_to_entity(row) for row in rows]

    def get_bucket_counts(self, list_type: RelationshipListType) -> dict[str, int]:
        counts = {bucket: 0 for bucket in ALL_BUCKETS}
        query = _COUNT_QUERIES[list_type]

        with self._db.connection() as conn:
            rows = conn.execute(query).fetchall()

        for row in rows:
            if row["bucket"] in counts:
                counts[row["bucket"]] = int(row["total"])
        return counts

    def get_by_pk(self, pk: str) -> InstagramProfile | None:
        with self._db.connection() as conn:
            row = conn.execute("SELECT * FROM profiles WHERE pk = ?", (pk,)).fetchone()
        return self._row_to_entity(row) if row is not None else None

    def save(self, profile: InstagramProfile) -> None:
        with self._db.connection() as conn:
            conn.execute(
                """
                UPDATE profiles
                SET username = ?,
                    full_name = ?,
                    bucket = ?,
                    profile_pic_url = ?,
                    is_following = ?,
                    is_follower = ?,
                    is_verified = ?
                WHERE pk = ?
                """,
                (
                    profile.username,
                    profile.full_name,
                    profile.bucket,
                    profile.profile_pic_url,
                    int(profile.is_following),
                    int(profile.is_follower),
                    int(profile.is_verified),
                    profile.pk,
                ),
            )

    @staticmethod
    def _row_to_entity(row: sqlite3.Row) -> InstagramProfile:
        return InstagramProfile(
            pk=row["pk"],
            username=row["username"],
            full_name=row["full_name"],
            profile_pic_url=row["profile_pic_url"],
            is_following=bool(row["is_following"]),
            is_follower=bool(row["is_follower"]),
            is_verified=bool(row["is_verified"]),
        )
