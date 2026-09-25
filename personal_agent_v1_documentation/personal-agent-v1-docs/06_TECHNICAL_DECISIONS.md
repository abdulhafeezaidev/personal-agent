# Personal Agent V1 — Technical Decisions / ADRs

## ADR-001 — Windows-first

Decision:
Build V1 for Windows.

Reason:
The target environment is the user's Windows laptop and the primary requirement is unattended desktop automation.

Status: Accepted.

## ADR-002 — No LLM in the automation core

Decision:
No LLM is required for workflow execution.

Reason:
Determinism, reliability, cost, privacy, and easier debugging.

Status: Accepted.

Future:
An LLM may later be added as an optional interface for creating/editing workflows, but it must produce explicit workflow data that is validated before execution.

## ADR-003 — Local-first

Decision:
V1 runs locally.

Reason:
The agent needs direct access to the Windows desktop and does not require a cloud backend for core functionality.

Status: Accepted.

## ADR-004 — Service + interactive desktop process

Decision:
Separate background lifecycle/scheduling from interactive GUI control.

Reason:
Windows services and interactive desktop sessions are different execution contexts.

Status: Accepted.

## ADR-005 — Browser automation over coordinate automation

Decision:
Prefer DOM/page-level browser automation.

Reason:
Coordinates are fragile when browser size/layout changes.

Status: Accepted.

## ADR-006 — UI Automation before coordinates

Decision:
Prefer Windows UI Automation/accessibility selectors before raw mouse coordinates.

Reason:
More robust desktop automation.

Status: Accepted.

## ADR-007 — No lock-screen bypass

Decision:
Do not implement lock-screen bypass.

Reason:
The unattended environment should be configured deliberately; the agent should not defeat Windows security boundaries.

Status: Accepted.

## ADR-008 — Fail closed

Decision:
When a critical expected state is not detected, stop instead of guessing.

Reason:
A wrong action can cause more damage than a failed workflow.

Status: Accepted.

## ADR-009 — One user

Decision:
V1 supports one local user.

Reason:
Avoid unnecessary authentication, permissions, and multi-user complexity.

Status: Accepted.

## ADR-010 — Minimal dependency surface

Decision:
Use mature Windows/browser automation technologies and minimize unnecessary dependencies.

Reason:
The project must remain understandable and maintainable by a small team.
