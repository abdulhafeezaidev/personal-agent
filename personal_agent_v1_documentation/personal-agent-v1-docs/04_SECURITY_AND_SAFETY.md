# Personal Agent V1 — Security and Safety Requirements

## 1. Threat model

This agent can control the user's computer. Therefore a bug is potentially more dangerous than a normal desktop application bug.

The design must minimize accidental destructive behavior.

## 2. Hard rules

The agent must NOT:
- bypass Windows authentication;
- bypass MFA;
- bypass CAPTCHA;
- extract passwords;
- scrape browser password stores;
- disable antivirus/security controls;
- modify security policy to gain control;
- install persistence outside the declared application design;
- execute hidden remote commands;
- expose the agent to the public internet by default;
- upload private files without an explicit workflow action;
- invent commands.

## 3. Command execution

If a future workflow supports shell/PowerShell commands:
- command execution must be an explicit workflow action;
- commands should be visible in the workflow;
- no natural-language-to-shell conversion in V1;
- log execution;
- require explicit configuration;
- never execute arbitrary content copied from a website.

## 4. Credentials

Do not store passwords in workflow JSON.

Do not ask the LLM builder to implement a custom password vault in V1.

If unattended Windows AutoLogon is configured, it must be treated as an explicit operating-system security tradeoff owned by the PC owner.

## 5. Destructive actions

For actions such as:
- deleting files,
- uninstalling applications,
- changing system settings,
- registry modification,

V1 should either not support them or require an explicit safety policy.

## 6. Browser security

The agent must not:
- defeat website security mechanisms;
- bypass access controls;
- circumvent authentication;
- solve CAPTCHAs automatically.

If an expected page is unavailable because authentication is required, fail clearly.

## 7. Kill switch

The user must have a way to stop active execution.

At minimum:
- UI Stop button
- process/service stop capability

A future emergency hotkey can be added.

## 8. Auditability

Every workflow execution should have:
- workflow ID
- workflow version
- timestamp
- step ID
- result
- error
- duration

## 9. Principle

The agent should be powerful because it is explicitly authorized, not because it bypasses security boundaries.
