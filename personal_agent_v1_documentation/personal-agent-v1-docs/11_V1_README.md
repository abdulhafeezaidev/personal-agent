# Personal Agent V1

A local-first deterministic Windows desktop automation agent.

## What it does

The agent executes explicitly defined workflows on a schedule.

Example:

```text
At 10:00 AM
  -> open LinkedIn
  -> open Gemini
  -> enter saved prompt
  -> wait
  -> copy output
  -> return to LinkedIn
  -> paste
  -> attach image
  -> publish
```

The workflow engine itself does not need an LLM.

## What makes V1 different

The system is designed around:

- deterministic execution
- explicit workflows
- local operation
- unattended Windows operation
- browser automation
- Windows UI Automation
- clear failure handling
- audit logs

## Current priority

Do not build the complete product at once.

First prove:

```text
Windows boot
  -> unattended user session
  -> agent startup
  -> simple GUI automation
  -> scheduled execution
```

Then expand.

## Important security note

The owner may intentionally configure Windows for unattended automatic logon. This carries a physical-security tradeoff. The agent itself must not bypass Windows authentication or other security controls.

## Development rule

Read the documentation in `docs/` before changing architecture or adding capabilities.
