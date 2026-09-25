# Personal Agent V1 — Product Requirements Document

## 1. Product

Personal Agent V1

## 2. Product type

Local-first deterministic desktop automation system for one Windows user.

## 3. Users

V1 has exactly one intended user: the owner of the PC.

## 4. Functional requirements

### FR-001 — Agent startup
The agent shall start automatically with Windows using an appropriate Windows-supported startup/service mechanism.

### FR-002 — Workflow storage
The system shall persist workflows locally.

Each workflow shall have:
- unique ID
- name
- enabled/disabled state
- schedule
- ordered steps
- creation/update timestamps
- version number

### FR-003 — Manual execution
The user shall be able to run any enabled workflow immediately.

### FR-004 — Scheduling
The user shall be able to schedule a workflow for:
- one-time execution
- daily execution
- weekly execution

V1 may limit recurrence options if needed, but the schedule model must not prevent future expansion.

### FR-005 — Workflow execution
The executor shall process steps in order.

The default behavior is:
- execute step
- verify success where verification exists
- continue
- on failure, follow the workflow's failure policy

### FR-006 — Application launch
The agent shall be able to launch a known application by configured executable/path or a supported Windows launch mechanism.

### FR-007 — URL launch
The agent shall open configured URLs using a selected browser.

### FR-008 — Wait
The agent shall support:
- fixed-duration wait
- condition-based wait where supported

Condition-based waits are preferred over arbitrary long sleeps.

### FR-009 — Keyboard
The agent shall support explicit keyboard actions such as:
- key press
- hotkey
- text typing

### FR-010 — Mouse
The agent shall support:
- click
- double click
- move
- drag where required

Coordinate-based mouse actions are a fallback, not the preferred mechanism.

### FR-011 — Clipboard
The agent shall support:
- copy
- paste
- read clipboard text where technically safe/appropriate

### FR-012 — File selection/upload
The agent shall support selecting a predefined local file through a standard file picker or browser upload mechanism.

### FR-013 — Browser interaction
The system shall support browser automation using stable page-level selectors where practical.

### FR-014 — Windows UI interaction
The system shall support Windows UI Automation for compatible desktop applications where practical.

### FR-015 — Screenshot/evidence
On failure, the agent should capture enough diagnostic information to understand the failure. Screenshots may be configurable.

### FR-016 — Execution logs
Every execution shall record:
- workflow
- start time
- end time
- status
- current step
- step result
- error information where applicable

### FR-017 — Stop
The user shall be able to request cancellation of an active workflow.

The executor shall stop at a safe boundary and record cancellation.

### FR-018 — Retry
A workflow step may optionally define a limited retry count.

Retries must never be infinite.

### FR-019 — Recovery
The workflow model shall allow a step to define:
- timeout
- retry count
- failure action

Possible failure actions:
- stop workflow
- skip step
- retry
- run recovery steps, if explicitly configured

### FR-020 — Transparency
The agent shall never silently perform an action that is not represented by the workflow.

## 5. Non-functional requirements

### NFR-001 Reliability
Prefer deterministic selectors and explicit verification over timing assumptions.

### NFR-002 Safety
Never execute arbitrary text as a shell command unless that action is explicitly represented and authorized in the workflow.

### NFR-003 Local-first
Workflow definitions and logs should remain local in V1 unless a future requirement explicitly introduces synchronization.

### NFR-004 Performance
The background agent should consume minimal CPU/memory while idle.

### NFR-005 Maintainability
Separate scheduling, workflow execution, desktop control, browser control, persistence, and UI.

### NFR-006 Observability
Failures must be diagnosable from logs.

### NFR-007 Determinism
The same workflow under the same desktop conditions should produce the same sequence of actions.

## 6. Acceptance criteria

The product cannot be called V1 complete until all critical acceptance tests in `08_ACCEPTANCE_TESTS.md` pass.
