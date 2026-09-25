# Personal Agent V1 — Implementation Plan

## Phase 0 — Environment proof

Goal:
Prove unattended Windows operation.

Tasks:
1. Confirm Windows version.
2. Confirm supported automatic logon configuration can be used on the owner's machine.
3. Configure power/sleep behavior for testing.
4. Create a tiny test program.
5. Reboot.
6. Verify the user session becomes available.
7. Verify the agent starts.
8. Verify it can open Notepad/Edge.
9. Verify GUI automation works without human intervention.

Exit criterion:
PC can reboot and reach an interactive session in the intended unattended test configuration, and the agent can perform a simple GUI action.

## Phase 1 — Agent skeleton

Build:
- solution/project structure
- service/background process
- desktop agent process
- local IPC
- local storage
- logging
- configuration

Exit criterion:
Agent starts, reports health, communicates between service and desktop process, and persists state.

## Phase 2 — Workflow engine

Build:
- workflow model
- JSON/schema validation
- executor
- timeouts
- retries
- failure policies
- cancellation
- execution history

Exit criterion:
A manually defined workflow can reliably execute a small sequence.

## Phase 3 — Automation adapters

Implement only:
- application launch
- URL launch
- wait
- keyboard
- mouse
- clipboard
- browser interaction
- Windows UI Automation
- file selection

Exit criterion:
Test workflow can operate Notepad and a browser.

## Phase 4 — Scheduler

Build:
- daily schedule
- one-time schedule
- weekly schedule
- duplicate-run prevention
- timezone handling
- missed-run behavior

Exit criterion:
Scheduled workflow executes at the configured time.

## Phase 5 — Basic UI

Build:
- dashboard
- workflow list
- workflow detail
- run now
- stop
- execution log
- settings

Exit criterion:
User can operate the system without touching configuration files.

## Phase 6 — Recorder

Build:
- record start/stop
- action capture
- captured-step review
- edit/delete step
- save workflow

Important:
The recorder must not automatically create hidden or unsupported actions.

Exit criterion:
User can record a simple workflow and replay it.

## Phase 7 — Real-world workflow

Implement one real workflow such as the LinkedIn/Gemini test.

Do not hard-code LinkedIn into the platform.

Exit criterion:
The real workflow runs successfully multiple times in a controlled test environment.

## Phase 8 — Reliability hardening

Test:
- browser closed
- browser already open
- slow network
- page load delay
- unexpected popup
- application not installed
- missing file
- locked session
- reboot
- workflow cancellation
- duplicate scheduler trigger

Exit criterion:
Failures are predictable, visible, and safe.

## Development rule

Complete one phase and pass its exit criteria before adding major functionality from the next phase.
