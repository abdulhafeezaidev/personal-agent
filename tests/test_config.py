"""
Unit tests for Configuration Management.
"""

import unittest
import tempfile
import json
from pathlib import Path
from personal_agent.config import AppConfig, load_config, get_project_root


class TestConfig(unittest.TestCase):
    def test_get_project_root(self):
        root = get_project_root()
        self.assertTrue(root.is_dir())
        self.assertTrue((root / "docs").is_dir())
        self.assertTrue((root / ".gitignore").is_file())

    def test_load_default_config(self):
        cfg = load_config()
        self.assertEqual(cfg.app_name, "Personal Agent")
        self.assertEqual(cfg.version, "1.0.0")
        self.assertEqual(cfg.ipc.pipe_name, r"\\.\pipe\personal_agent_ipc")
        self.assertTrue(Path(cfg.storage.db_path).is_absolute())
        self.assertTrue(Path(cfg.logging.service_log_path).is_absolute())

    def test_custom_config_loading(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_cfg_file = Path(tmp_dir) / "custom_config.json"
            data = {
                "app_name": "Test Agent",
                "version": "2.0.0",
                "environment": "test",
                "ipc": {"pipe_name": r"\\.\pipe\custom_test_pipe"},
                "storage": {"db_path": "custom_data/test.db"},
                "logging": {"log_level": "DEBUG"},
            }
            with open(tmp_cfg_file, "w", encoding="utf-8") as f:
                json.dump(data, f)

            cfg = load_config(tmp_cfg_file)
            self.assertEqual(cfg.app_name, "Test Agent")
            self.assertEqual(cfg.version, "2.0.0")
            self.assertEqual(cfg.environment, "test")
            self.assertEqual(cfg.ipc.pipe_name, r"\\.\pipe\custom_test_pipe")
            self.assertEqual(cfg.logging.log_level, "DEBUG")
            self.assertTrue(Path(cfg.storage.db_path).is_absolute())


if __name__ == "__main__":
    unittest.main()
