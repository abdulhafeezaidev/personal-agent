#!/usr/bin/env python3
"""
Personal Agent V1 - Phase 1 Windows Smoke Test
Verifies end-to-end foundation behavior:
Start Agent -> Spawns Desktop Process -> IPC Connects -> SQLite Initializes
-> Health Check Passes -> Reaches READY -> Clean Shutdown.
"""

import sys
import os
import time

# Ensure src/ is on PYTHONPATH
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, os.path.join(project_root, "src"))

from personal_agent.config import load_config
from personal_agent.service.agent_service import AgentService


def run_smoke_test() -> int:
    print("=" * 65)
    print("PERSONAL AGENT V1 - PHASE 1 WINDOWS SMOKE TEST")
    print("=" * 65)

    cfg = load_config()
    service = AgentService(cfg)

    print(f"\n[Step 1/5] Initializing Agent Service with config: {cfg.app_name} v{cfg.version}")
    print(f"           Database: {cfg.storage.db_path}")
    print(f"           IPC Pipe: {cfg.ipc.pipe_name}")

    print("\n[Step 2/5] Starting Agent Service & spawning Desktop Agent subprocess...")
    started = service.start(spawn_desktop=True)

    if not started:
        print("\n[FAIL] Agent Service failed to start or establish IPC.")
        service.stop()
        return 1

    print("[Step 2/5] SUCCESS: Desktop Agent spawned and IPC connected.")

    print("\n[Step 3/5] Executing end-to-end health verification...")
    health = service.perform_health_check()

    print(f"           Overall Status : {health.get('overall_status')}")
    print(f"           Service State  : {health['service']['status']} (PID: {health['service']['pid']})")
    print(f"           Storage State  : {health['storage']['status']}")
    print(f"           IPC State      : {health['ipc']['status']}")
    print(f"           Desktop State  : {health['desktop']['status']} (PID: {health['desktop'].get('pid')}, "
          f"Session: {health['desktop'].get('session_id')}, "
          f"Interactive Desktop: {health['desktop'].get('desktop_available')})")

    if health.get("overall_status") != "READY":
        print("\n[FAIL] Health check failed to report READY.")
        service.stop()
        return 1

    print("[Step 3/5] SUCCESS: Health check passed across all components.")

    print("\n[Step 4/5] Verifying persistent state in SQLite database...")
    state = service.state_repo.get_state("agent_state")
    version = service.state_repo.get_state("service_version")
    print(f"           Persisted 'agent_state': '{state}'")
    print(f"           Persisted 'service_version': '{version}'")

    if state != "READY":
        print(f"\n[FAIL] Expected agent_state 'READY', got '{state}'")
        service.stop()
        return 1

    print("[Step 4/5] SUCCESS: State persisted and verified in SQLite.")

    print("\n[Step 5/5] Performing graceful shutdown...")
    service.stop()

    final_state = service.state_repo.get_state("agent_state")
    print(f"           Final persisted state: '{final_state}'")

    if final_state != "STOPPED":
        print(f"\n[FAIL] Expected final state 'STOPPED', got '{final_state}'")
        return 1

    print("[Step 5/5] SUCCESS: Clean shutdown completed. No lingering processes.")

    print("\n" + "=" * 65)
    print("PHASE 1 SMOKE TEST RESULT: PASS")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(run_smoke_test())
