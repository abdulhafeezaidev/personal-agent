# Personal Agent V1

A local-first deterministic Windows desktop automation agent.

---

## Architecture Overview

```text
Windows OS
   │
   ├── Background / Service Agent (AgentService)
   │       ├── Process Lifecycle Coordinator
   │       ├── SQLite Local Storage (WAL mode, versioned migrations)
   │       ├── Structured Logging
   │       └── Dynamic Configuration
   │
   └── Interactive Desktop Agent (DesktopAgent)
           ├── Windows Session / Desktop Monitor (Win32 API)
           └── Future GUI / Browser Automation Worker

             ▲
             │ Local IPC (Windows Named Pipes: \\.\pipe\personal_agent_ipc)
             ▼

        Service <═════════════════════> Desktop Agent
```

---

## Implemented Phases

- [x] **Phase 0 — Environment Proof**:
  - Proved unattended Windows boot, supported Microsoft AutoLogon, interactive desktop accessibility, Notepad launch, deterministic input, readback verification, clean shutdown, and audit logging.
- [x] **Phase 1 — Agent Foundation & Local IPC**:
  - Established background/service and interactive desktop process boundaries.
  - Implemented Windows Named Pipe IPC with structured request/response protocol (`\\.\pipe\personal_agent_ipc`).
  - Implemented versioned SQLite database (`data/agent.db`) with WAL mode and repository patterns for `agent_state`, `workflows`, and `execution_runs`.
  - Implemented structured logging (`logs/agent_service.log`, `logs/agent_desktop.log`).
  - Implemented full lifecycle management and end-to-end health verification reporting `READY`.

---

## Running Diagnostics & Tests

### 1. Health Verification CLI
Run the end-to-end health check across all components:

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
Run the 13 automated unit tests:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

### 3. Windows Smoke Test
Run the end-to-end multi-process smoke test:

```powershell
$env:PYTHONPATH = "src"
python scripts/smoke_test.py
```

---

## Security & Safety Guardrails

- **Zero Network Exposure**: No TCP ports or network listeners are opened; IPC uses Windows local Named Pipes strictly on the local machine.
- **Zero Credential Storage**: No passwords, tokens, or private secrets are stored in databases, configuration files, or logs.
- **No LLM in Automation Core**: Workflow execution is completely deterministic and local.
- **Fail Closed**: Inability to contact the desktop agent or verify an interactive desktop causes the agent to enter `DEGRADED` status rather than guessing.
