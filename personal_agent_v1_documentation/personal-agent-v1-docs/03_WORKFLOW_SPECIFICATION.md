# Personal Agent V1 — Workflow Specification

## 1. Principle

A workflow is a deterministic sequence of explicit actions.

It is data, not code.

## 2. Example schema

```json
{
  "id": "daily-linkedin-post",
  "name": "Daily LinkedIn Post",
  "version": 1,
  "enabled": true,
  "schedule": {
    "type": "daily",
    "time": "10:00"
  },
  "steps": [
    {
      "id": "step-001",
      "action": "open_url",
      "url": "https://www.linkedin.com",
      "timeout_ms": 30000,
      "retry_count": 1,
      "on_failure": "stop"
    },
    {
      "id": "step-002",
      "action": "wait",
      "duration_ms": 5000
    }
  ]
}
```

## 3. V1 action types

### Application
- `launch_app`
- `close_app`

### Browser
- `open_url`
- `click_locator`
- `type_locator`
- `select_file_locator`
- `wait_for_locator`

### Windows UI
- `find_ui_element`
- `click_ui_element`
- `type_ui_element`
- `wait_for_ui_element`

### Input
- `click`
- `double_click`
- `move`
- `drag`
- `key_press`
- `hotkey`
- `type_text`

### Clipboard
- `copy`
- `paste`
- `read_text`

### File
- `select_file`
- `wait_for_file`

### Control
- `wait`
- `screenshot`
- `assert`
- `stop`

Only implement actions that are actually required. Do not build a giant action catalog before the first workflow works.

## 4. Step fields

Common optional fields:

```text
id
action
timeout_ms
retry_count
on_failure
description
```

Action-specific fields contain the actual target.

## 5. Verification

Where possible, every important action should have a verifiable outcome.

Example:

```text
click "Start a post"
    ↓
verify post editor exists
```

Do not assume that a click succeeded merely because the mouse click was sent.

## 6. Timing

Avoid:

```text
sleep 30 seconds
```

when a condition can be detected.

Prefer:

```text
wait until "post editor" exists
timeout 30 seconds
```

Fixed waits remain available when external services genuinely require them.

## 7. Credentials

The workflow specification must not contain:
- Windows passwords
- browser passwords
- authentication tokens
- API secrets

Authentication should rely on the already-authenticated user session or a future dedicated secure credential mechanism.

## 8. Versioning

Workflow changes increment the workflow version.

Execution logs should record the exact workflow version used.

## 9. Example LinkedIn workflow

This is illustrative and must be validated against the live site during implementation:

```text
1. Open LinkedIn.
2. Verify LinkedIn is loaded.
3. Open/create-post UI.
4. Open Gemini.
5. Verify Gemini is available.
6. Enter predefined prompt.
7. Wait for generation completion.
8. Copy generated text.
9. Return to LinkedIn.
10. Paste text.
11. Select predefined image.
12. Verify media is attached.
13. Submit/publish.
14. Verify post-completion state.
15. Record success.
```

If the website presents a CAPTCHA, MFA challenge, unexpected consent dialog, or other authentication/security challenge, stop and report it rather than attempting to bypass it.
