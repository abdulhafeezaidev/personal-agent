# Personal Agent V1 — UI Specification

## 1. Goal

The UI should be simple enough that the owner can create and monitor deterministic workflows without programming.

## 2. Main screen

Display:

```text
PERSONAL AGENT

Agent status: RUNNING

Next scheduled workflow:
Daily LinkedIn Post — 10:00 AM

Workflows
--------------------------------
Daily LinkedIn Post
Daily — 10:00 AM
Status: Enabled
Last run: Success
[Run Now] [Edit] [Disable]

Morning Workspace
Daily — 8:30 AM
Status: Enabled
Last run: Success
[Run Now] [Edit] [Disable]

[ + Create Workflow ]
```

## 3. Workflow creation

V1 should support two approaches:

### Option A — Manual workflow editor
User adds steps from supported actions.

### Option B — Recorder
Preferred future/early V1 feature:
- press Record
- perform actions
- stop recording
- inspect captured steps
- save workflow

The recorder must show what it captured before saving.

## 4. Workflow detail

Display:
- name
- schedule
- enabled state
- steps
- retry/failure policy
- last execution
- execution history

## 5. Execution view

Display:
- current workflow
- current step
- elapsed time
- current status
- recent events
- Stop button

Example:

```text
Running: Daily LinkedIn Post

✓ Open LinkedIn
✓ Open Gemini
✓ Enter prompt
● Waiting for response...
○ Copy result
○ Return to LinkedIn
○ Publish

[ STOP ]
```

## 6. Failure view

Show:

```text
Workflow failed

Step: Copy Gemini response
Reason: Expected element was not found
Elapsed: 42s

[View Details]
[Retry]
[Stop]
```

Do not hide failures behind generic "Something went wrong."

## 7. Settings

Minimum:
- startup behavior
- logging level
- default browser
- screenshot-on-failure
- data directory
- timezone
- unattended mode status
- service/desktop-agent status

## 8. UI philosophy

No unnecessary AI/chat interface in V1.

This is an automation control panel, not a chatbot.
