# Architecture Diagnose

> **Adapting this skill.** Configure it by running `/sigrid:setup` to set your customer, system, and conventions in the profile — these survive plugin updates.

Finds the one directory in a Sigrid system most worth fixing structurally, and names the concrete
fix — or reports that nothing qualifies. Grounded in Sigrid's measured dependency graph, not code
reading. Diagnoses only; asks before any change is made.

For an in-progress diff instead of the whole system, use `architecture-drift`.

## Prerequisites

- Sigrid MCP plugin
- Sigrid customer and system name in the profile (`/sigrid:setup`)

## Usage

```
/sigrid:architecture-diagnose
```
