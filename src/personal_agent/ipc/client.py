"""
Personal Agent V1 - Named Pipe IPC Client
Connects to local Named Pipe server, sends requests, and receives correlated responses.
"""

from __future__ import annotations

import logging
import time
from multiprocessing.connection import Client
from typing import Any
from personal_agent.ipc.protocol import IPCRequest, IPCResponse


class NamedPipeClient:
    """
    Windows Named Pipe Client using Python standard library AF_PIPE transport.
    """

    def __init__(
        self,
        pipe_name: str,
        auth_key: str = "personal_agent_local_v1",
        timeout_seconds: float = 5.0,
        logger: logging.Logger | None = None,
    ) -> None:
        self.pipe_name = pipe_name
        self.auth_key = auth_key.encode("utf-8")
        self.timeout_seconds = timeout_seconds
        self.logger = logger or logging.getLogger("personal_agent.ipc.client")

    def send_request(self, request: IPCRequest, timeout: float | None = None) -> IPCResponse:
        """
        Send a request over the named pipe and wait for the correlated response.
        Raises TimeoutError on timeout, ConnectionError on connection failure.
        """
        effective_timeout = timeout or self.timeout_seconds
        self.logger.info(
            f"Sending IPC request: type={request.type} to {self.pipe_name}",
            extra={"request_id": request.request_id},
        )

        try:
            conn = Client(
                self.pipe_name,
                family="AF_PIPE",
                authkey=self.auth_key,
            )
        except Exception as ex:
            self.logger.error(
                f"Failed to connect to IPC pipe {self.pipe_name}: {ex}",
                extra={"request_id": request.request_id},
            )
            raise ConnectionError(f"Cannot connect to IPC pipe {self.pipe_name}: {ex}") from ex

        try:
            conn.send_bytes(request.to_bytes())

            # Poll with timeout
            if not conn.poll(effective_timeout):
                self.logger.error(
                    f"IPC request timed out after {effective_timeout}s",
                    extra={"request_id": request.request_id},
                )
                raise TimeoutError(f"IPC request {request.request_id} timed out waiting for response")

            raw_resp = conn.recv_bytes()
            response = IPCResponse.from_bytes(raw_resp)
            self.logger.info(
                f"Received IPC response: status={response.status}",
                extra={"request_id": response.request_id},
            )
            return response
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def check_connection(self, max_attempts: int = 5, retry_interval: float = 0.5) -> bool:
        """Probe whether the pipe server is reachable."""
        for _ in range(max_attempts):
            try:
                conn = Client(self.pipe_name, family="AF_PIPE", authkey=self.auth_key)
                conn.close()
                return True
            except Exception:
                time.sleep(retry_interval)
        return False
