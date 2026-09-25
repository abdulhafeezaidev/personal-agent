"""
Unit tests for Lifecycle and Health Check.
"""

import unittest
import tempfile
import uuid
from pathlib import Path
from personal_agent.config import AppConfig, IPCConfig, StorageConfig, LoggingConfig
from personal_agent.service.agent_service import AgentService
from personal_agent.desktop.desktop_agent import DesktopAgent


class TestLifecycle(unittest.TestCase):
    def test_service_desktop_lifecycle_and_health(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            unique_pipe = rf"\\.\pipe\test_lifecycle_{uuid.uuid4().hex[:8]}"

            cfg = AppConfig(
                app_name="LifecycleTestAgent",
                version="1.0.0",
                environment="test",
                ipc=IPCConfig(pipe_name=unique_pipe, auth_key="test_auth", timeout_seconds=3.0),
                storage=StorageConfig(db_path=str(tmp_path / "test_lifecycle.db")),
                logging=LoggingConfig(
                    service_log_path=str(tmp_path / "service.log"),
                    desktop_log_path=str(tmp_path / "desktop.log"),
                ),
            )

            service = AgentService(cfg)
            desktop = DesktopAgent(cfg)

            # Start desktop agent in background thread for unit test
            desktop.start()

            try:
                # Start service without spawning subprocess (using our in-process desktop)
                started = service.start(spawn_desktop=False)
                self.assertTrue(started)

                state = service.state_repo.get_state("agent_state")
                self.assertEqual(state, "READY")

                report = service.perform_health_check()
                self.assertEqual(report["overall_status"], "READY")
                self.assertEqual(report["service"]["status"], "ok")
                self.assertEqual(report["storage"]["status"], "ok")
                self.assertEqual(report["ipc"]["status"], "ok")
                self.assertEqual(report["desktop"]["status"], "ok")
                self.assertEqual(report["desktop"]["process"], "desktop_agent")
                self.assertIsNotNone(report["desktop"]["session_id"])

                # Stop service
                service.stop()
                final_state = service.state_repo.get_state("agent_state")
                self.assertEqual(final_state, "STOPPED")
            finally:
                desktop.stop()
                import logging
                logging.shutdown()


if __name__ == "__main__":
    unittest.main()
