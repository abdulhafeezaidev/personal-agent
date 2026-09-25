# Personal Agent — V1 Project Charter

## 1. Purpose

Build a Windows-first personal desktop automation agent that can execute deterministic, pre-recorded workflows without an LLM in the agent core.

The first release is intentionally narrow. The agent should reliably execute scheduled workflows on the user's own Windows PC while the user is away.

## 2. Core principle

**The agent executes instructions; it does not invent instructions.**

For V1:
- No LLM reasoning inside the automation engine.
- No autonomous task planning.
- No guessing what the user meant.
- No self-modifying workflows.
- No hidden behavior.
- Every workflow consists of explicit, ordered steps.
- The agent must fail safely when a required step cannot be completed.

## 3. Primary V1 use case

A scheduled workflow can:
1. Start/open applications or websites.
2. Wait for a specified condition or duration.
3. Interact with browser pages and desktop applications.
4. Type predefined text.
5. Use clipboard operations.
6. Select/upload files.
7. Execute predefined keyboard/mouse/UI actions.
8. Complete the workflow.
9. Record execution status and errors.

Example:
Windows starts -> user session becomes available through an intentionally configured unattended Windows setup -> agent starts -> scheduled workflow opens browser -> opens Gemini -> enters a saved prompt -> obtains/copies output -> returns to LinkedIn -> creates a post -> attaches a predefined image -> publishes.

The LinkedIn workflow is a validation example, not a hard-coded feature.

## 4. V1 non-goals

Do NOT build:
- LLM-based planning.
- Voice assistant.
- General conversational assistant.
- Computer vision-based autonomous reasoning.
- Self-learning.
- Automatic workflow invention.
- Credential/password extraction.
- Security bypasses.
- CAPTCHA bypass.
- MFA bypass.
- DRM/security circumvention.
- Malware-like persistence.
- Remote-control server.
- Cloud backend unless technically required later.
- Multi-user support.
- Mobile app.
- Cross-platform support.

## 5. Definition of success

V1 is successful when a user can:
- create/save a workflow,
- run it manually,
- schedule it,
- restart the PC,
- have the configured Windows user session become available without user intervention,
- have the agent start,
- have the scheduled workflow execute against the interactive desktop,
- see whether it succeeded or failed,
- inspect the execution log,
- safely stop an active workflow.

## 6. Platform

Target: Windows 10/11, with Windows 11 as the primary development/test target.

The implementation should use native Windows capabilities where appropriate.

## 7. Guiding engineering rule

When a requirement is ambiguous, do NOT invent behavior. Stop and mark the ambiguity as a decision required from the owner.
