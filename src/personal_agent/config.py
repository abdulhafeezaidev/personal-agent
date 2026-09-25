"""
Personal Agent V1 - Configuration Management
Handles project-root discovery, structured configuration schemas,
and path resolution without hardcoding local directories.
"""

from __future__ import annotations

import os
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


def get_project_root() -> Path:
    """
    Discover project root dynamically by traversing up from this file
    or using the PERSONAL_AGENT_ROOT environment variable.
    """
    env_root = os.environ.get("PERSONAL_AGENT_ROOT")
    if env_root and Path(env_root).is_dir():
        return Path(env_root).resolve()

    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "docs").is_dir() and (parent / ".gitignore").is_file():
            return parent

    # Fallback to grandparent of this file (src/personal_agent -> D:/Personal Agent)
    return current.parent.parent.resolve()


@dataclass
class IPCConfig:
    pipe_name: str = r"\\.\pipe\personal_agent_ipc"
    timeout_seconds: float = 5.0
    auth_key: str = "personal_agent_local_v1"


@dataclass
class StorageConfig:
    db_path: str = "data/agent.db"
    wal_mode: bool = True


@dataclass
class LoggingConfig:
    log_level: str = "INFO"
    service_log_path: str = "logs/agent_service.log"
    desktop_log_path: str = "logs/agent_desktop.log"


@dataclass
class AppConfig:
    app_name: str = "Personal Agent"
    version: str = "1.0.0"
    environment: str = "development"
    ipc: IPCConfig = field(default_factory=IPCConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def resolve_paths(self, root: Path | None = None) -> AppConfig:
        """Resolve all relative paths against the project root."""
        base = root or get_project_root()
        resolved_db = (base / self.storage.db_path).resolve() if not Path(self.storage.db_path).is_absolute() else Path(self.storage.db_path)
        resolved_service_log = (base / self.logging.service_log_path).resolve() if not Path(self.logging.service_log_path).is_absolute() else Path(self.logging.service_log_path)
        resolved_desktop_log = (base / self.logging.desktop_log_path).resolve() if not Path(self.logging.desktop_log_path).is_absolute() else Path(self.logging.desktop_log_path)

        self.storage.db_path = str(resolved_db)
        self.logging.service_log_path = str(resolved_service_log)
        self.logging.desktop_log_path = str(resolved_desktop_log)
        return self


def load_config(config_path: Path | str | None = None) -> AppConfig:
    """Load configuration from JSON file or return defaults with resolved paths."""
    root = get_project_root()
    if config_path is None:
        config_path = root / "config" / "agent_config.json"
    else:
        config_path = Path(config_path)

    if config_path.is_file():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)

            ipc_data = data.get("ipc", {})
            storage_data = data.get("storage", {})
            logging_data = data.get("logging", {})

            cfg = AppConfig(
                app_name=data.get("app_name", "Personal Agent"),
                version=data.get("version", "1.0.0"),
                environment=data.get("environment", "development"),
                ipc=IPCConfig(**ipc_data),
                storage=StorageConfig(**storage_data),
                logging=LoggingConfig(**logging_data),
            )
            return cfg.resolve_paths(root)
        except Exception:
            # Fall back to safe defaults if file is malformed
            return AppConfig().resolve_paths(root)

    cfg = AppConfig()
    return cfg.resolve_paths(root)


def save_default_config(target_path: Path | str | None = None) -> Path:
    """Write default configuration file to disk if not present."""
    root = get_project_root()
    if target_path is None:
        target_path = root / "config" / "agent_config.json"
    else:
        target_path = Path(target_path)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    cfg = AppConfig()
    data = asdict(cfg)

    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return target_path
