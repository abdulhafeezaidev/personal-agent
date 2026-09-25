"""
Personal Agent V1 - Interactive Desktop Agent Process
Executes inside the interactive Windows user session and serves requests over local Named Pipe IPC.
"""

from __future__ import annotations

import os
import sys
import time
import signal
import threading
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from personal_agent.config import AppConfig, load_config
from personal_agent.logging import setup_logger
from personal_agent.ipc.protocol import IPCRequest, IPCResponse
from personal_agent.ipc.server import NamedPipeServer

# Win32 API Constants
DESKTOP_SWITCHDESKTOP = 0x0100


def get_windows_session_info() -> dict[str, Any]:
    """Retrieve session ID and desktop accessibility using native Win32 APIs."""
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    pid = kernel32.GetCurrentProcessId()
    session_id = wintypes.DWORD()
    kernel32.ProcessIdToSessionId(pid, ctypes.byref(session_id))

    desktop_available = False
    hdesk = user32.OpenInputDesktop(0, False, DESKTOP_SWITCHDESKTOP)
    if hdesk:
        desktop_available = True
        user32.CloseDesktop(hdesk)

    desktop_hwnd = user32.GetDesktopWindow()

    return {
        "pid": pid,
        "session_id": session_id.value,
        "desktop_available": desktop_available,
        "desktop_hwnd": desktop_hwnd,
        "username": f"{os.environ.get('USERDOMAIN', '')}\\{os.environ.get('USERNAME', '')}",
    }


class DesktopAgent:
    """
    Interactive Desktop Agent that runs in user desktop context
    and handles IPC requests from the Service component.
    """

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or load_config()
        self.logger = setup_logger(
            component="desktop",
            log_file_path=self.config.logging.desktop_log_path,
            log_level=self.config.logging.log_level,
        )
        self.server = NamedPipeServer(
            pipe_name=self.config.ipc.pipe_name,
            auth_key=self.config.ipc.auth_key,
            logger=self.logger,
        )
        self._stop_event = threading.Event()
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register IPC message handlers."""
        self.server.register_handler("health_check", self._handle_health_check)
        self.server.register_handler("ping", self._handle_ping)
        self.server.register_handler("shutdown", self._handle_shutdown)

    def _handle_health_check(self, request: IPCRequest) -> IPCResponse:
        """Handle health_check request by verifying desktop status."""
        self.logger.info("Executing health_check handler", extra={"request_id": request.request_id})
        session_info = get_windows_session_info()
        payload = {
            "process": "desktop_agent",
            "version": self.config.version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **session_info,
            "status": "READY" if session_info["desktop_available"] else "DEGRADED",
        }
        return IPCResponse.ok(request.request_id, payload)

    def _handle_ping(self, request: IPCRequest) -> IPCResponse:
        """Simple ping/pong handler."""
        return IPCResponse.ok(
            request.request_id,
            {"pong": True, "timestamp": datetime.now(timezone.utc).isoformat()},
        )

    def _handle_shutdown(self, request: IPCRequest) -> IPCResponse:
        """Handle request to gracefully stop the desktop agent."""
        self.logger.info("Shutdown requested via IPC", extra={"request_id": request.request_id})

        def deferred_stop():
            time.sleep(0.2)
            self.stop()

        threading.Thread(target=deferred_stop, daemon=True).start()
        return IPCResponse.ok(request.request_id, {"status": "shutting_down"})

    def start(self) -> None:
        """Start IPC server and block until stop is requested."""
        self.logger.info(
            f"Desktop Agent starting (PID: {os.getpid()}, Version: {self.config.version})"
        )
        self.server.start()
        self.logger.info("Desktop Agent ready and listening for IPC connections")

    def run_forever(self) -> None:
        """Run until stop event is signaled."""
        self.start()
        try:
            while not self._stop_event.is_set():
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.logger.info("Desktop Agent received keyboard interrupt")
            self.stop()

    def stop(self) -> None:
        """Stop desktop agent and close IPC."""
        if self._stop_event.is_set():
            return
        self.logger.info("Desktop Agent stopping...")
        self._stop_event.set()
        self.server.stop()
        self.logger.info("Desktop Agent stopped cleanly.")

        # Release file handlers
        raw_logger = getattr(self.logger, "logger", self.logger)
        for h in list(raw_logger.handlers):
            h.close()
            raw_logger.removeHandler(h)


def main() -> None:
    """CLI entrypoint for standalone desktop agent execution."""
    agent = DesktopAgent()

    def sig_handler(sig, frame):
        agent.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    agent.run_forever()


if __name__ == "__main__":
    main()
