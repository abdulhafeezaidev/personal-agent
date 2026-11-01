# Personal Agent V1

A local-first, deterministic Windows desktop automation agent and process lifecycle coordinator.

---

## Architecture Overview

```text
+-------------------------------------------------------------------------------+
|                                  Windows OS                                   |
|                                                                               |
|   +------------------------------------+   +------------------------------+   |
|   |  Background Service (AgentService) |   | Interactive Desktop Agent    |   |
|   |                                    |   | (DesktopAgent)               |   |
|   |  - Process Lifecycle Coordinator   |   |                              |   |
|   |  - SQLite Storage (WAL, Migrations)|   |  - Win32 Session & Desktop   |   |
|   |  - Structured Logging & Audit Trail|   |    Monitor (user32/kernel32) |   |
|   |  - Dynamic Configuration           |   |  - Deterministic Automation  |   |
|   +-----------------+------------------+   +--------------+---------------+   |
|                     |                                     |                   |
|                     +------------[ Local IPC ]------------+                   |
|                      Windows Named Pipe: \\.\pipe\personal_agent_ipc          |
+-------------------------------------------------------------------------------+
```

---

## Core Capabilities

- **Strict Multi-Process Isolation**: Decoupled background supervisor service from interactive desktop worker via Windows Named Pipes (`\\.\pipe\personal_agent_ipc`).
- **Win32 Interactive Desktop Verification**: Validates interactive user sessions, desktop window stations (`winsta0\default`), and process tokens before attempting UI automation.
- **Transactional SQLite Storage with WAL**: Multi-connection safe storage in Write-Ahead Logging mode (`WAL`) with automated schema migrations for `agent_state`, `workflows`, and `execution_runs`.
- **Structured Audit Logging**: Dedicated rotating log channels for both service and desktop components (`logs/agent_service.log`, `logs/agent_desktop.log`).
- **Deterministic Process Control**: Zero hallucinated commands or unpredictable loops; built with explicit state machines and strict health checks (`READY`, `BUSY`, `DEGRADED`, `SHUTDOWN`).

---

## Implemented Engineering Milestones

- [x] **Phase 0 — Unattended Environment Proof**:
  - Validated headless-to-interactive transition, Microsoft AutoLogon support, interactive desktop accessibility, Notepad execution, deterministic input injection, readback verification, clean teardown, and audit logging.
- [x] **Phase 1 — Agent Foundation & Local IPC**:
  - Established background/service and interactive desktop process boundaries.
  - Implemented Windows Named Pipe IPC with structured request/response framing protocol.
  - Implemented versioned SQLite database with WAL mode and repository pattern (`agent_state`, `workflows`, `execution_runs`).
  - Implemented multi-process lifecycle management and health check CLI reporting `READY`.

---

## Technology Stack

- **Language**: Python 3.12+ / 3.14
- **OS Subsystem**: Windows NT / Win32 API (`ctypes`, `win32api`, `win32con`, `win32pipe`, `win32file`)
- **Storage**: SQLite 3 with Write-Ahead Logging (WAL) and automatic versioned migrations
- **IPC Protocol**: Windows Named Pipes (`\\.\pipe\personal_agent_ipc`) with length-prefixed JSON serialization
- **Testing**: `pytest`, `unittest` with 100% passing unit & IPC integration tests

---

## Project Structure

```text
personal-agent/
├── config/
│   └── agent_config.json        # Runtime agent configuration
├── data/
│   └── agent.db                 # SQLite database (WAL mode)
├── docs/                        # Specifications (Architecture, Security, Acceptance Tests)
│   ├── 00_PROJECT_CHARTER.md
│   ├── 01_PRODUCT_REQUIREMENTS.md
│   ├── 02_ARCHITECTURE.md
│   ├── 03_WORKFLOW_SPECIFICATION.md
│   ├── 04_SECURITY_AND_SAFETY.md
│   └── ...
├── logs/                        # Structured log sinks
├── scripts/
│   ├── phase0_proof.py          # Phase 0 execution proof
│   └── smoke_test.py            # Multi-process end-to-end smoke test
├── src/
│   └── personal_agent/
│       ├── cli.py               # Health & inspection CLI
│       ├── config.py            # Pydantic-style typed configuration
│       ├── logging.py           # Structured logger setup
│       ├── desktop/             # Win32 desktop monitor & automation
│       ├── ipc/                 # Named Pipe server, client, and wire protocol
│       ├── service/             # Supervisor service & lifecycle coordinator
│       └── storage/             # SQLite database, migrations, and repositories
└── tests/                       # Unit & integration test suite
```

---

## Running Diagnostics & Tests

### 1. Health Verification CLI
Run the end-to-end health check across all runtime components:

```powershell
$env:PYTHONPATH = "src"
python -m personal_agent.cli health
```

Example output:
```text
Personal Agent
State: READY

Background: OK (PID: 3796)
Desktop:    OK (PID: 6828, Session: 1, Interactive: True)
IPC:        OK (Named Pipe: \\.\pipe\personal_agent_ipc)
SQLite:     OK (D:\Personal Agent\data\agent.db)
```

### 2. Automated Test Suite
Run the 13 automated unit and integration tests:

```powershell
$env:PYTHONPATH = "src"
pytest tests -v
```

### 3. Windows Multi-Process Smoke Test
Run the end-to-end multi-process lifecycle smoke test:

```powershell
$env:PYTHONPATH = "src"
python scripts/smoke_test.py
```

---

## Security & Safety Guardrails

- **Zero Network Exposure**: No TCP/UDP ports or remote listeners are opened; IPC is bound strictly to local Windows Named Pipes.
- **Zero Credential Persistence**: No credentials, tokens, or private secrets stored in database, logs, or configuration files.
- **Deterministic Execution**: Zero stochastic execution paths in automation core; workflows are strictly validated against pre-declared schemas.
- **Fail-Closed Design**: If the supervisor loses contact with the interactive desktop session, it immediately enters `DEGRADED` status rather than guessing.
