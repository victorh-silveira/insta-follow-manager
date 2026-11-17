"""SQLite database connection and schema initialization."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
import sqlite3

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS profiles (
    pk TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    full_name TEXT NOT NULL,
    bucket TEXT NOT NULL,
    profile_pic_url TEXT,
    is_following INTEGER NOT NULL DEFAULT 0,
    is_follower INTEGER NOT NULL DEFAULT 0,
    is_verified INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_profiles_bucket ON profiles (bucket);
CREATE INDEX IF NOT EXISTS idx_profiles_flags ON profiles (is_following, is_follower);
"""


class SQLiteDatabase:
    """Lightweight SQLite connection manager."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        with self.connection() as conn:
            conn.executescript(SCHEMA_SQL)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Yield a SQLite connection with Row factory and automatic commit/close."""
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
