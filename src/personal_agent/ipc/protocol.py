"""
Personal Agent V1 - IPC Protocol
Defines structured request and response message contracts for local Named Pipe IPC.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class IPCRequest:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: f"req-{uuid.uuid4().hex[:12]}")

    def to_bytes(self) -> bytes:
        data = {
            "request_id": self.request_id,
            "type": self.type,
            "payload": self.payload,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> IPCRequest:
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("IPC payload must be a JSON object")
        if "type" not in data:
            raise ValueError("IPC request missing 'type' field")
        return cls(
            request_id=data.get("request_id", f"req-{uuid.uuid4().hex[:12]}"),
            type=str(data["type"]),
            payload=data.get("payload", {}) if isinstance(data.get("payload"), dict) else {},
        )


@dataclass
class IPCResponse:
    request_id: str
    status: str  # "ok" or "error"
    payload: dict[str, Any] = field(default_factory=dict)
    error: Optional[dict[str, str]] = None

    def to_bytes(self) -> bytes:
        data = {
            "request_id": self.request_id,
            "status": self.status,
            "payload": self.payload,
        }
        if self.error:
            data["error"] = self.error
        return json.dumps(data).encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> IPCResponse:
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("IPC payload must be a JSON object")
        return cls(
            request_id=data.get("request_id", ""),
            status=data.get("status", "error"),
            payload=data.get("payload", {}) if isinstance(data.get("payload"), dict) else {},
            error=data.get("error"),
        )

    @classmethod
    def ok(cls, request_id: str, payload: Optional[dict[str, Any]] = None) -> IPCResponse:
        return cls(request_id=request_id, status="ok", payload=payload or {})

    @classmethod
    def fail(cls, request_id: str, code: str, message: str) -> IPCResponse:
        return cls(
            request_id=request_id,
            status="error",
            payload={},
            error={"code": code, "message": message},
        )
