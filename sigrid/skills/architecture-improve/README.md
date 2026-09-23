# Architecture Improve

> **Adapting this skill.** Configure it by running `/sigrid:setup` to set your customer, system, and conventions in the profile — these survive plugin updates.

Implements the fix `architecture-diagnose` named: moves or splits files, adds a facade, reroutes
calls — then verifies the result against Sigrid's numbers. Makes code changes.

Reads the handover doc `architecture-diagnose` wrote. With none present, runs
`architecture-diagnose` first.

## Prerequisites

- A handover doc from `architecture-diagnose` (or let this skill run that first)
- Sigrid MCP plugin
- Sigrid customer and system name in the profile (`/sigrid:setup`)
- Build and test commands for the repo

## Usage

```
/sigrid:architecture-improve
```
