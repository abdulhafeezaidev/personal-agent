"""
Personal Agent V1 - Schema Migrations
Applies versioned database migrations deterministically.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable
from personal_agent.storage.database import Database

# Migration definitions: (version, name, SQL script)
MIGRATIONS: list[tuple[int, str, str]] = [
    (
        1,
        "initial_foundation_schema",
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agent_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            schedule_type TEXT,
            schedule_expr TEXT,
            steps_json TEXT NOT NULL DEFAULT '[]',
            version INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS execution_runs (
            id TEXT PRIMARY KEY,
            workflow_id TEXT,
            status TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            current_step INTEGER DEFAULT 0,
            error_message TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_workflows_enabled ON workflows(enabled);
        CREATE INDEX IF NOT EXISTS idx_execution_runs_workflow_id ON execution_runs(workflow_id);
        CREATE INDEX IF NOT EXISTS idx_execution_runs_status ON execution_runs(status);
        """
    )
]


class MigrationRunner:
    """Manages tracking and applying database migrations."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def get_applied_versions(self) -> set[int]:
        """Return set of applied migration versions."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Check if schema_migrations table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations';"
            )
            if not cursor.fetchone():
                return set()

            cursor.execute("SELECT version FROM schema_migrations ORDER BY version ASC;")
            return {row["version"] for row in cursor.fetchall()}

    def apply_migrations(self) -> int:
        """Apply all pending migrations. Returns count of applied migrations."""
        applied = self.get_applied_versions()
        count = 0

        for version, name, sql in MIGRATIONS:
            if version not in applied:
                now_utc = datetime.now(timezone.utc).isoformat()
                with self.db.transaction() as cursor:
                    cursor.executescript(sql)
                    cursor.execute(
                        "INSERT INTO schema_migrations (version, name, applied_at) VALUES (?, ?, ?);",
                        (version, name, now_utc)
                    )
                count += 1

        return count
