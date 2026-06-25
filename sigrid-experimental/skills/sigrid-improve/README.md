# Sigrid Improve

> **Experimental** — this skill is under active development and will change. Use it directly from the plugin, copy and adapt it to your own workflow, or treat it as a reference for building your own skills. See SKILL.md for the full procedure.
>
> Adaptation ideas: change the guardrail threshold, restrict which property types are auto-fixed, or add project-specific invariants.

Executes refactoring candidates identified by Sigrid. Works in two modes: autonomous (runs all candidates, you review diffs at the end) or interactive (you steer priorities one step at a time).

## What it does

1. Takes diagnosis output from `sigrid-diagnose` (or runs it first)
2. Applies refactoring to each candidate
3. Validates changes against Sigrid guardrails
4. Reports results with before/after metrics

## Prerequisites

- Sigrid MCP plugin (`code_quality_guardrails`)
- Sigrid customer and system name in context (e.g. CLAUDE.md)
- Run `sigrid-diagnose` first, or let this skill trigger it

## Usage

```
/sigrid-experimental:sigrid-improve
```
