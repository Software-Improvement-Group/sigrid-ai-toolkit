# Sigrid Improve

> **Adapting this skill.** Configure it by running `/sigrid:setup` to record any behavior preferences in the profile (e.g. off-limits areas, project-specific invariants) — these survive plugin updates.

Executes refactoring candidates identified by Sigrid. Works in two modes: autonomous (runs all candidates, you review diffs at the end) or interactive (you steer priorities one step at a time).

## What it does

1. Takes diagnosis output from `sigrid-diagnose` (or runs it first)
2. Applies refactoring to each candidate
3. Validates changes against Sigrid guardrails
4. Reports results with before/after metrics

## Prerequisites

- Sigrid MCP plugin (`code_quality_guardrails`)
- Sigrid customer and system name in the profile (`/sigrid:setup`)
- Run `sigrid-diagnose` first, or let this skill trigger it

## Usage

```
/sigrid:sigrid-improve
```
