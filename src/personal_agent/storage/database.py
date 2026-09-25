"""
Personal Agent V1 - SQLite Database Connection Manager
Provides thread-safe connection management, WAL mode, and transaction contexts.
"""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class Database:
    """Manages SQLite database connections and configuration."""

    def __init__(self, db_path: str | Path, wal_mode: bool = True) -> None:
        self.db_path = Path(db_path).resolve()
        self.wal_mode = wal_mode
        self._local = threading.local()

        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_pragmas()

    def _initialize_pragmas(self) -> None:
        """Run initial database pragmas on first access."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            if self.wal_mode:
                cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
            conn.commit()

    @contextmanager
    def get_connection(self) -> Iterator[sqlite3.Connection]:
        """Provide a connection with row factory enabled."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=10.0,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Cursor]:
        """Provide a transactional cursor that commits or rolls back automatically."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except Exception:
                conn.rollback()
                raise
