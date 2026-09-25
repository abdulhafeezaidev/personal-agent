"""
Unit tests for SQLite Storage, Migrations, and Repositories.
"""

import unittest
import tempfile
from pathlib import Path
from personal_agent.storage.database import Database
from personal_agent.storage.migrations import MigrationRunner
from personal_agent.storage.repositories import (
    StateRepository,
    WorkflowRepository,
    ExecutionRepository,
)


class TestStorage(unittest.TestCase):
    def test_database_initialization_and_wal(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            db = Database(db_path, wal_mode=True)
            self.assertTrue(db_path.exists())

            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA journal_mode;")
                mode = cursor.fetchone()[0]
                self.assertEqual(mode.lower(), "wal")

    def test_migrations_runner(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db = Database(Path(tmp_dir) / "test.db")
            runner = MigrationRunner(db)

            applied = runner.apply_migrations()
            self.assertEqual(applied, 1)
            self.assertIn(1, runner.get_applied_versions())

            # Re-applying should apply 0
            self.assertEqual(runner.apply_migrations(), 0)

    def test_state_repository(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db = Database(Path(tmp_dir) / "test.db")
            MigrationRunner(db).apply_migrations()

            repo = StateRepository(db)
            repo.set_state("status", "READY")
            self.assertEqual(repo.get_state("status"), "READY")

            repo.set_state("status", "STOPPED")
            self.assertEqual(repo.get_state("status"), "STOPPED")

            all_state = repo.get_all()
            self.assertEqual(all_state.get("status"), "STOPPED")

    def test_workflow_repository(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db = Database(Path(tmp_dir) / "test.db")
            MigrationRunner(db).apply_migrations()

            repo = WorkflowRepository(db)
            wf = repo.create(
                workflow_id="wf-001",
                name="Daily Notepad Proof",
                enabled=True,
                schedule_type="daily",
                steps=[{"action": "open_app", "target": "notepad.exe"}],
            )

            self.assertEqual(wf["id"], "wf-001")
            self.assertEqual(wf["name"], "Daily Notepad Proof")
            self.assertTrue(wf["enabled"])
            self.assertEqual(len(wf["steps"]), 1)

            all_wfs = repo.list_all()
            self.assertEqual(len(all_wfs), 1)
            self.assertEqual(all_wfs[0]["id"], "wf-001")

    def test_execution_repository(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db = Database(Path(tmp_dir) / "test.db")
            MigrationRunner(db).apply_migrations()

            repo = ExecutionRepository(db)
            run = repo.create(run_id="run-100", workflow_id=None, status="PENDING")
            self.assertEqual(run["id"], "run-100")
            self.assertEqual(run["status"], "PENDING")

            repo.update(run_id="run-100", status="COMPLETED", current_step=3)
            updated = repo.get("run-100")
            self.assertIsNotNone(updated)
            self.assertEqual(updated["status"], "COMPLETED")
            self.assertEqual(updated["current_step"], 3)


if __name__ == "__main__":
    unittest.main()
