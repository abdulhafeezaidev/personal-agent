"""
Unit tests for Named Pipe IPC Protocol, Server, and Client.
"""

import unittest
import time
import uuid
from personal_agent.ipc.protocol import IPCRequest, IPCResponse
from personal_agent.ipc.server import NamedPipeServer
from personal_agent.ipc.client import NamedPipeClient


class TestIPC(unittest.TestCase):
    def test_ipc_protocol_serialization(self):
        req = IPCRequest(type="health_check", payload={"test": 123}, request_id="req-999")
        raw = req.to_bytes()
        decoded = IPCRequest.from_bytes(raw)
        self.assertEqual(decoded.type, "health_check")
        self.assertEqual(decoded.payload, {"test": 123})
        self.assertEqual(decoded.request_id, "req-999")

        resp = IPCResponse.ok(request_id="req-999", payload={"status": "all_good"})
        raw_resp = resp.to_bytes()
        decoded_resp = IPCResponse.from_bytes(raw_resp)
        self.assertEqual(decoded_resp.status, "ok")
        self.assertEqual(decoded_resp.payload, {"status": "all_good"})
        self.assertIsNone(decoded_resp.error)

    def test_ipc_named_pipe_roundtrip(self):
        unique_pipe = rf"\\.\pipe\test_ipc_roundtrip_{uuid.uuid4().hex[:8]}"
        server = NamedPipeServer(pipe_name=unique_pipe, auth_key="test_auth")

        def echo_handler(req: IPCRequest) -> IPCResponse:
            return IPCResponse.ok(req.request_id, {"echo": req.payload.get("data")})

        server.register_handler("echo", echo_handler)
        server.start()

        try:
            client = NamedPipeClient(pipe_name=unique_pipe, auth_key="test_auth", timeout_seconds=3.0)
            self.assertTrue(client.check_connection(max_attempts=10, retry_interval=0.1))

            req = IPCRequest(type="echo", payload={"data": "hello_windows"})
            resp = client.send_request(req)

            self.assertEqual(resp.status, "ok")
            self.assertEqual(resp.request_id, req.request_id)
            self.assertEqual(resp.payload.get("echo"), "hello_windows")
        finally:
            server.stop()

    def test_ipc_unknown_request_type(self):
        unique_pipe = rf"\\.\pipe\test_ipc_unknown_{uuid.uuid4().hex[:8]}"
        server = NamedPipeServer(pipe_name=unique_pipe, auth_key="test_auth")
        server.start()

        try:
            client = NamedPipeClient(pipe_name=unique_pipe, auth_key="test_auth", timeout_seconds=3.0)
            self.assertTrue(client.check_connection(max_attempts=10, retry_interval=0.1))

            req = IPCRequest(type="unregistered_command")
            resp = client.send_request(req)

            self.assertEqual(resp.status, "error")
            self.assertIsNotNone(resp.error)
            self.assertEqual(resp.error["code"], "UNKNOWN_REQUEST_TYPE")
        finally:
            server.stop()

    def test_ipc_timeout(self):
        unique_pipe = rf"\\.\pipe\test_ipc_timeout_{uuid.uuid4().hex[:8]}"
        server = NamedPipeServer(pipe_name=unique_pipe, auth_key="test_auth")

        def slow_handler(req: IPCRequest) -> IPCResponse:
            time.sleep(1.0)
            return IPCResponse.ok(req.request_id, {})

        server.register_handler("slow", slow_handler)
        server.start()

        try:
            client = NamedPipeClient(pipe_name=unique_pipe, auth_key="test_auth", timeout_seconds=0.2)
            self.assertTrue(client.check_connection(max_attempts=10, retry_interval=0.1))

            req = IPCRequest(type="slow")
            with self.assertRaises(TimeoutError):
                client.send_request(req, timeout=0.2)
        finally:
            server.stop()


if __name__ == "__main__":
    unittest.main()
