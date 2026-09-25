"""
Personal Agent V1 - Named Pipe IPC Server
Listens for incoming local Named Pipe connections and dispatches requests.
"""

from __future__ import annotations

import logging
import threading
import time
from multiprocessing.connection import Listener
from typing import Callable, Any
from personal_agent.ipc.protocol import IPCRequest, IPCResponse

HandlerFunc = Callable[[IPCRequest], IPCResponse]


class NamedPipeServer:
    """
    Windows Named Pipe Server using Python standard library AF_PIPE transport.
    """

    def __init__(
        self,
        pipe_name: str,
        auth_key: str = "personal_agent_local_v1",
        logger: logging.Logger | None = None,
    ) -> None:
        self.pipe_name = pipe_name
        self.auth_key = auth_key.encode("utf-8")
        self.logger = logger or logging.getLogger("personal_agent.ipc.server")
        self._handlers: dict[str, HandlerFunc] = {}
        self._listener: Listener | None = None
        self._running = False
        self._thread: threading.Thread | None = None

    def register_handler(self, request_type: str, handler: HandlerFunc) -> None:
        """Register a handler callback for a specific request type."""
        self._handlers[request_type] = handler

    def start(self) -> None:
        """Start listening for connections in a background daemon thread."""
        if self._running:
            return

        self._running = True
        self._listener = Listener(
            self.pipe_name,
            family="AF_PIPE",
            authkey=self.auth_key,
        )
        self.logger.info(f"IPC Server listening on Named Pipe: {self.pipe_name}")

        self._thread = threading.Thread(target=self._serve_loop, daemon=True, name="IPCServerThread")
        self._thread.start()

    def _serve_loop(self) -> None:
        """Continuously accept connections and handle requests."""
        while self._running and self._listener:
            try:
                conn = self._listener.accept()
            except (OSError, EOFError):
                if not self._running:
                    break
                continue

            # Handle connection in a dedicated thread to support quick client interactions
            client_thread = threading.Thread(
                target=self._handle_client,
                args=(conn,),
                daemon=True,
                name="IPCClientHandler",
            )
            client_thread.start()

    def _handle_client(self, conn: Any) -> None:
        """Process messages on an accepted connection."""
        try:
            while self._running:
                try:
                    raw_bytes = conn.recv_bytes()
                except (EOFError, ConnectionResetError, OSError):
                    break

                try:
                    request = IPCRequest.from_bytes(raw_bytes)
                    self.logger.info(
                        f"Received IPC request: type={request.type}",
                        extra={"request_id": request.request_id},
                    )

                    handler = self._handlers.get(request.type)
                    if handler:
                        response = handler(request)
                    else:
                        response = IPCResponse.fail(
                            request.request_id,
                            "UNKNOWN_REQUEST_TYPE",
                            f"No handler registered for request type: {request.type}",
                        )
                except Exception as ex:
                    self.logger.exception(f"Error handling IPC request: {ex}")
                    response = IPCResponse.fail(
                        "unknown",
                        "INTERNAL_ERROR",
                        str(ex),
                    )

                try:
                    conn.send_bytes(response.to_bytes())
                    self.logger.info(
                        f"Sent IPC response: status={response.status}",
                        extra={"request_id": response.request_id},
                    )
                except (BrokenPipeError, ConnectionResetError, OSError):
                    self.logger.warning(
                        "Client disconnected before IPC response could be delivered.",
                        extra={"request_id": response.request_id},
                    )
                    break
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def stop(self) -> None:
        """Stop the IPC server and close listener."""
        self._running = False
        if self._listener:
            try:
                self._listener.close()
            except Exception:
                pass
            self._listener = None

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self.logger.info("IPC Server stopped.")
