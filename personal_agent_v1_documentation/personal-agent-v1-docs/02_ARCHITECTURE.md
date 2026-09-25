# Personal Agent V1 — Architecture

## 1. Architecture goal

Create a small, local Windows system with clear separation between scheduling, workflow execution, machine control, and the user interface.

## 2. Proposed architecture

```text
                    Windows PC
                        |
                +-------+--------+
                |                |
        Agent Service       Agent Desktop
                |                |
        +-------+-------+   +----+----------------+
        |               |   |          |           |
    Scheduler       Workflow   Windows UI     Browser
                    Engine     Automation     Automation
        |               |          |              |
        +---------------+----------+--------------+
                        |
                  Local Storage
              workflows + settings
                  + execution logs
```

## 3. Components

### 3.1 Agent Service
Responsibilities:
- lifecycle
- scheduling
- coordination
- health state
- communication with desktop process

The service must NOT directly assume it can manipulate an interactive desktop session.

### 3.2 Agent Desktop
Responsibilities:
- execute interactive GUI actions in the user's Windows session
- keyboard/mouse
- Windows UI Automation
- browser automation
- clipboard
- screenshots/diagnostics

### 3.3 Scheduler
Responsibilities:
- calculate due workflows
- trigger workflows
- prevent accidental duplicate execution
- persist last-run state

### 3.4 Workflow Engine
Responsibilities:
- load workflow
- validate workflow
- execute steps sequentially
- enforce timeout/retry/failure policies
- emit structured execution events

### 3.5 Automation Adapters

The executor should use adapters rather than embedding automation code everywhere.

Suggested interfaces/concepts:

```text
AutomationAdapter
  -> WindowsUIAdapter
  -> BrowserAdapter
  -> InputAdapter
  -> ClipboardAdapter
  -> FileAdapter
```

### 3.6 Persistence
Use a local database or structured local files. SQLite is preferred if available and appropriate.

Store:
- workflows
- schedules
- settings
- execution history
- application configuration

Do not store raw passwords.

## 4. Interaction hierarchy

Use the most reliable mechanism available:

1. Browser DOM/locator automation.
2. Windows UI Automation/accessibility tree.
3. Application-specific automation interface.
4. Keyboard shortcuts.
5. Mouse coordinates as final fallback.

## 5. Interactive session requirement

GUI automation requires an interactive desktop session.

The architecture therefore treats:
- Windows service/background execution
- interactive desktop automation

as separate concerns.

The service should detect when a usable interactive session is unavailable and report a clear state instead of pretending the workflow succeeded.

## 6. Unattended Windows requirement

The PC may be configured by the owner for supported automatic logon so that a Windows user session is available after boot.

This is a machine configuration decision, not an agent feature.

The agent must not implement password extraction, login bypass, or secure-desktop circumvention.

## 7. Lock state

V1 should not attempt to bypass the Windows lock screen.

For unattended GUI workflows, the machine configuration should prevent the intended automation window from becoming unusable through sleep/lock policies.

If a workflow encounters a locked or unavailable desktop:
- do not claim success,
- record a specific environment/session error,
- stop or retry according to explicit policy.

## 8. Browser strategy

Use browser automation with stable selectors whenever possible.

Do not build critical workflows around screen coordinates when a reliable DOM locator exists.

## 9. Process isolation

The service and desktop agent should communicate through a local authenticated mechanism appropriate for Windows, such as named pipes or another local IPC mechanism.

Do not expose an unauthenticated network listener.

## 10. Failure philosophy

A wrong action is worse than a skipped action.

When uncertain:
- verify,
- retry within limits,
- otherwise stop safely.

Never "guess and continue."
