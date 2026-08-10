# Architecture Drift

> **Adapting this skill.** Configure it by running `/sigrid:setup` to set your customer, system, and conventions in the profile — these survive plugin updates.

Flags architecture drift in an in-progress change (a git diff, staged change, or feature branch) by
checking new dependencies against Sigrid's measured architecture graph — not code-reading heuristics.

## What it does

1. Reads the diff to find new cross-directory imports, calls, and type references
2. Grounds each one against Sigrid's current dependency structure (`architecture:get_external_dependencies`, `architecture:get_internal`)
3. Flags references that don't match any existing edge, close a new cycle, or bypass a facade/gateway
4. Reports what to change and why — or confirms the change is architecturally clean

This is a lightweight, diff-scoped check. For a full system-wide coupling/cohesion audit, use a
heavier workflow instead.

## Prerequisites

- Sigrid MCP plugin (`architecture:get_internal`, `architecture:get_external_dependencies`)
- Sigrid customer and system name in the profile (`/sigrid:setup`)

## Usage

```
/sigrid:architecture-drift
```

Trigger phrases: "does this change introduce bad coupling", "check my diff/PR for architecture
drift", "will this break our module boundaries", "did I bypass the gateway/facade", "is this new
dependency safe", or "what depends on this file".
