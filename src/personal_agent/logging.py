"""
Personal Agent V1 - Structured Logging
Provides component-aware structured logging to file and console.
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class StructuredFormatter(logging.Formatter):
    """
    Format log records with standard structured fields:
    ISO-8601 UTC timestamp, level, component, request_id, and message.
    """

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        component = getattr(record, "component", "agent")
        request_id = getattr(record, "request_id", "-")

        base_msg = f"{timestamp} [{record.levelname:<5}] [{component}] [req:{request_id}] {record.getMessage()}"
        if record.exc_info:
            base_msg += "\n" + self.formatException(record.exc_info)
        return base_msg


def setup_logger(
    component: str,
    log_file_path: str | Path | None = None,
    log_level: str = "INFO",
    enable_console: bool = True,
) -> logging.Logger:
    """
    Configure and return a structured logger for a given component.
    """
    logger_name = f"personal_agent.{component}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.handlers.clear()
    logger.propagate = False

    formatter = StructuredFormatter()

    if log_file_path:
        file_path = Path(log_file_path).resolve()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(file_path, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Attach default component adapter
    return ComponentLoggerAdapter(logger, {"component": component})


class ComponentLoggerAdapter(logging.LoggerAdapter):
    """
    Ensures 'component' and optional 'request_id' fields are always present.
    """

    def process(self, msg: Any, kwargs: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
        extra = kwargs.setdefault("extra", {})
        if "component" not in extra:
            extra["component"] = self.extra.get("component", "agent")
        if "request_id" not in extra:
            extra["request_id"] = "-"
        return msg, kwargs
