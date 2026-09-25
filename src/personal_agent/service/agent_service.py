"""
Personal Agent V1 - Background/Service Agent Coordinator
Coordinates storage, lifecycle, background state, and IPC communication
with the Interactive Desktop Agent.
"""

from __future__ import annotations

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Any, Optional

from personal_agent.config import AppConfig, load_config
from personal_agent.logging import setup_logger
from personal_agent.storage.database import Database
from personal_agent.storage.migrations import MigrationRunner
from personal_agent.storage.repositories import StateRepository
from personal_agent.ipc.protocol import IPCRequest, IPCResponse
from personal_agent.ipc.client import NamedPipeClient


class AgentService:
    """
    Background/Service coordinator representing the lifecycle, state,
    and storage foundation.
    """

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or load_config()
        self.logger = setup_logger(
            component="service",
            log_file_path=self.config.logging.service_log_path,
            log_level=self.config.logging.log_level,
        )

        # Storage initialization
        self.database = Database(
            db_path=self.config.storage.db_path,
            wal_mode=self.config.storage.wal_mode,
        )
        self.migration_runner = MigrationRunner(self.database)
        self.state_repo = StateRepository(self.database)

        # IPC client for communicating with desktop agent
        self.ipc_client = NamedPipeClient(
            pipe_name=self.config.ipc.pipe_name,
            auth_key=self.config.ipc.auth_key,
            timeout_seconds=self.config.ipc.timeout_seconds,
            logger=self.logger,
        )

        self._desktop_process: Optional[subprocess.Popen] = None
        self._running = False

    def initialize_storage(self) -> None:
        """Run migrations and verify database health."""
        applied_count = self.migration_runner.apply_migrations()
        self.logger.info(f"Database migrations applied: {applied_count}")
        self.state_repo.set_state("service_version", self.config.version)
        self.state_repo.set_state("environment", self.config.environment)

    def start_desktop_agent_process(self) -> subprocess.Popen:
        """
        Launch the interactive desktop agent in a separate process.
        """
        self.logger.info("Spawning Desktop Agent process...")
        script_path = Path(__file__).resolve().parent.parent / "desktop" / "desktop_agent.py"
        python_exe = sys.executable

        proc = subprocess.Popen(
            [python_exe, str(script_path)],
            cwd=str(Path(self.config.storage.db_path).parent.parent),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._desktop_process = proc
        self.logger.info(f"Desktop Agent spawned with PID: {proc.pid}")
        return proc

    def start(self, spawn_desktop: bool = True) -> bool:
        """
        Start the agent service, initialize database, connect to Desktop Agent,
        and verify full health check.
        """
        self.logger.info("=" * 60)
        self.logger.info(f"STARTING {self.config.app_name} V{self.config.version} (PID: {os.getpid()})")
        self.logger.info("=" * 60)

        # 1. Initialize storage
        self.initialize_storage()
        self.state_repo.set_state("agent_state", "STARTING")

        # 2. Start desktop process if requested
        if spawn_desktop and not self._desktop_process:
            self.start_desktop_agent_process()

        # 3. Wait for IPC pipe readiness
        self.logger.info("Waiting for Desktop Agent IPC connection...")
        pipe_ready = self.ipc_client.check_connection(max_attempts=10, retry_interval=0.5)
        if not pipe_ready:
            self.logger.error("Failed to establish IPC connection with Desktop Agent.")
            self.state_repo.set_state("agent_state", "ERROR_IPC")
            return False

        self.logger.info("IPC connection established with Desktop Agent.")

        # 4. Perform health check
        health_report = self.perform_health_check()
        if health_report.get("status") == "ok":
            self.state_repo.set_state("agent_state", "READY")
            self._running = True
            self.logger.info("Personal Agent reached READY state.")
            return True
        else:
            self.state_repo.set_state("agent_state", "DEGRADED")
            self.logger.warning("Agent started with DEGRADED health status.")
            return False

    def perform_health_check(self) -> dict[str, Any]:
        """
        Execute end-to-end health verification across Service, SQLite, IPC, and Desktop.
        """
        report: dict[str, Any] = {
            "app_name": self.config.app_name,
            "version": self.config.version,
            "service": {"status": "ok", "pid": os.getpid()},
            "storage": {"status": "error"},
            "ipc": {"status": "error"},
            "desktop": {"status": "error"},
            "overall_status": "error",
        }

        # Check SQLite
        try:
            val = self.state_repo.get_state("service_version")
            if val == self.config.version:
                report["storage"] = {"status": "ok", "db_path": self.config.storage.db_path}
        except Exception as ex:
            report["storage"] = {"status": "error", "error": str(ex)}

        # Check Desktop via IPC
        try:
            req = IPCRequest(type="health_check")
            resp = self.ipc_client.send_request(req, timeout=3.0)
            if resp.status == "ok":
                report["ipc"] = {"status": "ok"}
                desktop_healthy = (
                    resp.payload.get("process") == "desktop_agent"
                    and resp.payload.get("desktop_available") is True
                )
                payload_data = dict(resp.payload)
                desktop_state = payload_data.pop("status", "READY")
                report["desktop"] = {
                    "status": "ok" if desktop_healthy else "degraded",
                    "desktop_state": desktop_state,
                    **payload_data,
                }
            else:
                report["ipc"] = {"status": "error", "details": resp.error}
        except Exception as ex:
            report["ipc"] = {"status": "error", "error": str(ex)}

        # Overall calculation
        if (
            report["service"]["status"] == "ok"
            and report["storage"]["status"] == "ok"
            and report["ipc"]["status"] == "ok"
            and report["desktop"]["status"] == "ok"
        ):
            report["status"] = "ok"
            report["overall_status"] = "READY"
        else:
            report["status"] = "degraded"
            report["overall_status"] = "DEGRADED"

        return report

    def stop(self) -> None:
        """Perform clean, graceful shutdown of all components."""
        self.logger.info("Stopping Agent Service...")
        self.state_repo.set_state("agent_state", "STOPPING")

        # Send shutdown to desktop agent over IPC
        try:
            req = IPCRequest(type="shutdown")
            self.ipc_client.send_request(req, timeout=2.0)
            self.logger.info("Sent shutdown signal to Desktop Agent via IPC.")
        except Exception as ex:
            self.logger.warning(f"Could not deliver graceful shutdown to Desktop Agent: {ex}")

        # Wait for desktop process to exit if spawned by us
        if self._desktop_process:
            try:
                self._desktop_process.wait(timeout=3.0)
                self.logger.info("Desktop Agent process exited cleanly.")
            except subprocess.TimeoutExpired:
                self.logger.warning("Desktop Agent process did not terminate within timeout; terminating.")
                self._desktop_process.terminate()
            self._desktop_process = None

        self.state_repo.set_state("agent_state", "STOPPED")
        self._running = False
        self.logger.info("Agent Service stopped cleanly.")

        # Release file handlers
        raw_logger = getattr(self.logger, "logger", self.logger)
        for h in list(raw_logger.handlers):
            h.close()
            raw_logger.removeHandler(h)
