# Personal Agent V1 — Acceptance Tests

## AT-001 — Startup
Given Windows boots,
when the configured user session is available,
then the agent starts automatically.

## AT-002 — Agent health
Given the agent is running,
then the UI reports a healthy/running state.

## AT-003 — Launch application
Given a workflow contains launch_app,
when executed,
then the configured application opens.

## AT-004 — Open URL
Given a workflow contains open_url,
when executed,
then the configured URL opens.

## AT-005 — Keyboard
Given a workflow contains a keyboard action,
when executed,
then the intended key/text action occurs.

## AT-006 — Clipboard
Given clipboard content is available,
when the workflow pastes it,
then the target receives the expected content.

## AT-007 — Browser selector
Given a browser element exists,
when a locator action runs,
then the element is interacted with without relying on screen coordinates.

## AT-008 — UI Automation
Given a compatible Windows UI element exists,
when the workflow targets it,
then the action succeeds.

## AT-009 — Timeout
Given an expected element never appears,
then the step times out rather than waiting forever.

## AT-010 — Retry
Given a step has retry_count=2,
when it fails,
then it is attempted no more than the configured number of retries.

## AT-011 — Failure
Given a critical step fails,
then the workflow records failure and does not falsely report success.

## AT-012 — Stop
Given a workflow is running,
when the user selects Stop,
then execution terminates safely and records cancellation.

## AT-013 — Daily schedule
Given a workflow is scheduled daily,
when the configured time arrives,
then it runs once for that scheduled occurrence.

## AT-014 — Duplicate prevention
Given the scheduler checks multiple times around the same minute,
then it does not launch duplicate executions for the same scheduled occurrence.

## AT-015 — Reboot
Given the machine is rebooted,
then the configured unattended environment becomes available and the agent returns to a usable state.

## AT-016 — Locked session
Given the Windows session is locked,
then the agent does not falsely report GUI workflow success and records an unavailable-session error.

## AT-017 — Missing file
Given a workflow requires a missing upload file,
then the workflow fails clearly and does not upload a different file.

## AT-018 — Unexpected UI
Given a required target cannot be verified,
then the agent stops according to the workflow failure policy.

## AT-019 — Execution history
Given a workflow runs,
then its start/end/status/step results are visible in execution history.

## AT-020 — No hidden AI
Given the V1 system is executed,
then no LLM is required for the workflow engine to execute its predefined actions.

## AT-021 — Security boundary
Given a website presents CAPTCHA/MFA/authentication challenge,
then the workflow stops instead of attempting to bypass the challenge.

## AT-022 — Real workflow
Given the validated LinkedIn/Gemini workflow,
when all prerequisites are available,
then the workflow completes the configured sequence and verifies the final state.

## Release gate

All critical tests must pass before calling the build V1.
