# Personal Agent V1 — Repository Structure

The exact language/framework may be chosen during Phase 0 after verifying the machine and available tooling, but the logical structure should remain separated.

Suggested structure:

```text
personal-agent/
|
+-- docs/
|   +-- 00_PROJECT_CHARTER.md
|   +-- 01_PRODUCT_REQUIREMENTS.md
|   +-- 02_ARCHITECTURE.md
|   +-- 03_WORKFLOW_SPECIFICATION.md
|   +-- 04_SECURITY_AND_SAFETY.md
|   +-- 05_UI_SPECIFICATION.md
|   +-- 06_TECHNICAL_DECISIONS.md
|   +-- 07_IMPLEMENTATION_PLAN.md
|   +-- 08_ACCEPTANCE_TESTS.md
|   +-- 09_BUILDER_RULES.md
|   +-- 10_REPOSITORY_STRUCTURE.md
|
+-- src/
|   +-- Agent.Service/
|   +-- Agent.Desktop/
|   +-- Agent.Core/
|   +-- Agent.Automation/
|   |   +-- Browser/
|   |   +-- WindowsUI/
|   |   +-- Input/
|   |   +-- Clipboard/
|   |   +-- Files/
|   +-- Agent.Scheduler/
|   +-- Agent.Storage/
|   +-- Agent.UI/
|
+-- tests/
|   +-- Agent.Core.Tests/
|   +-- Agent.Scheduler.Tests/
|   +-- Agent.Automation.Tests/
|   +-- Integration/
|
+-- workflows/
|   +-- examples/
|
+-- logs/
|
+-- README.md
```

This is a logical target, not permission to create every directory immediately.

Only create components when the current implementation phase requires them.
