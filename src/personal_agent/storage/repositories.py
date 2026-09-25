"""
Personal Agent V1 - Storage Repositories
Provides clean data access patterns for agent state, workflows, and execution runs.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional
from personal_agent.storage.database import Database


class StateRepository:
    """Stores key-value pairs representing agent operational state."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def get_state(self, key: str) -> Optional[str]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM agent_state WHERE key = ?;", (key,))
            row = cursor.fetchone()
            return row["value"] if row else None

    def set_state(self, key: str, value: str) -> None:
        now_utc = datetime.now(timezone.utc).isoformat()
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO agent_state (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at;
                """,
                (key, value, now_utc)
            )

    def get_all(self) -> dict[str, str]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM agent_state;")
            return {row["key"]: row["value"] for row in cursor.fetchall()}


class WorkflowRepository:
    """Manages workflow metadata records."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def create(
        self,
        workflow_id: str,
        name: str,
        enabled: bool = True,
        schedule_type: Optional[str] = None,
        schedule_expr: Optional[str] = None,
        steps: Optional[list[dict[str, Any]]] = None,
        version: int = 1,
    ) -> dict[str, Any]:
        now_utc = datetime.now(timezone.utc).isoformat()
        steps_json = json.dumps(steps or [])

        with self.db.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO workflows (id, name, enabled, schedule_type, schedule_expr, steps_json, version, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (workflow_id, name, 1 if enabled else 0, schedule_type, schedule_expr, steps_json, version, now_utc, now_utc)
            )

        return self.get(workflow_id)  # type: ignore

    def get(self, workflow_id: str) -> Optional[dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workflows WHERE id = ?;", (workflow_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["enabled"] = bool(data["enabled"])
            data["steps"] = json.loads(data.pop("steps_json"))
            return data

    def list_all(self) -> list[dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workflows ORDER BY created_at ASC;")
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                data["enabled"] = bool(data["enabled"])
                data["steps"] = json.loads(data.pop("steps_json"))
                results.append(data)
            return results


class ExecutionRepository:
    """Manages execution run logs and status records."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def create(
        self,
        run_id: str,
        workflow_id: Optional[str],
        status: str = "PENDING",
        current_step: int = 0,
    ) -> dict[str, Any]:
        now_utc = datetime.now(timezone.utc).isoformat()
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO execution_runs (id, workflow_id, status, start_time, current_step, created_at)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (run_id, workflow_id, status, now_utc, current_step, now_utc)
            )
        return self.get(run_id)  # type: ignore

    def update(
        self,
        run_id: str,
        status: str,
        current_step: Optional[int] = None,
        error_message: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> None:
        with self.db.transaction() as cursor:
            updates = ["status = ?"]
            params: list[Any] = [status]

            if current_step is not None:
                updates.append("current_step = ?")
                params.append(current_step)

            if error_message is not None:
                updates.append("error_message = ?")
                params.append(error_message)

            if end_time is not None:
                updates.append("end_time = ?")
                params.append(end_time)

            params.append(run_id)
            query = f"UPDATE execution_runs SET {', '.join(updates)} WHERE id = ?;"
            cursor.execute(query, tuple(params))

    def get(self, run_id: str) -> Optional[dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM execution_runs WHERE id = ?;", (run_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
