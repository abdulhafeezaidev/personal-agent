"""
Personal Agent V1 - Developer & Diagnostic CLI
Provides commands for running health checks, checking status, and running the agent.
"""

from __future__ import annotations

import sys
import time
import argparse
from personal_agent.config import load_config
from personal_agent.service.agent_service import AgentService


def cmd_health() -> int:
    """Run full end-to-end health check and print human-readable summary."""
    cfg = load_config()
    service = AgentService(cfg)
    print("=" * 50)
    print(f"Personal Agent Health Verification (V{cfg.version})")
    print("=" * 50)

    # Start service components
    started = service.start(spawn_desktop=True)
    report = service.perform_health_check()

    print(f"\nPersonal Agent")
    print(f"State: {report.get('overall_status', 'UNKNOWN')}\n")

    bg_status = "OK" if report["service"]["status"] == "ok" else "FAIL"
    desktop_status = "OK" if report["desktop"]["status"] == "ok" else "FAIL"
    ipc_status = "OK" if report["ipc"]["status"] == "ok" else "FAIL"
    db_status = "OK" if report["storage"]["status"] == "ok" else "FAIL"

    print(f"Background: {bg_status} (PID: {report['service']['pid']})")
    desktop_details = report["desktop"]
    if desktop_status == "OK":
        print(
            f"Desktop:    {desktop_status} (PID: {desktop_details.get('pid')}, "
            f"Session: {desktop_details.get('session_id')}, "
            f"Interactive: {desktop_details.get('desktop_available')})"
        )
    else:
        print(f"Desktop:    {desktop_status}")

    print(f"IPC:        {ipc_status} (Named Pipe: {cfg.ipc.pipe_name})")
    print(f"SQLite:     {db_status} ({cfg.storage.db_path})")

    # Clean shutdown
    service.stop()
    print("\nClean shutdown completed.")
    return 0 if started else 1


def cmd_run() -> int:
    """Run agent service until interrupted."""
    cfg = load_config()
    service = AgentService(cfg)
    if not service.start(spawn_desktop=True):
        print("Failed to start agent service.")
        return 1

    print("Agent Service is RUNNING. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopping Agent Service...")
    finally:
        service.stop()

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Personal Agent CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("health", help="Run end-to-end health check")
    subparsers.add_parser("run", help="Run agent service")

    args = parser.parse_args()
    if args.command == "health" or args.command is None:
        sys.exit(cmd_health())
    elif args.command == "run":
        sys.exit(cmd_run())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
