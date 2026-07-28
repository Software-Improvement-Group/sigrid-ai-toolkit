# Sigrid Diagnose

> **Adapting this skill.** Configure it by running `/sigrid:setup` to set your customer, system, and conventions in the profile — these survive plugin updates.
>
> Pairs with `sigrid-improve` — diagnose first, then act.

Guided maintainability diagnosis for a Sigrid system. Identifies the weakest quality property, explains the structural patterns behind it, and surfaces the highest-leverage refactoring candidates.

## What it does

1. Retrieves maintainability ratings from Sigrid
2. Fetches refactoring candidates across all properties
3. Cross-references findings to identify multi-property hotspots
4. Presents a prioritized action plan

This skill is diagnosis only — it does not make code changes. Use `sigrid-improve` to act on its output.

## Prerequisites

- Sigrid MCP plugin (`maintainability_ratings`, `refactoring_candidates`)
- Sigrid customer and system name in the profile (`/sigrid:setup`)

## Usage

```
/sigrid:sigrid-diagnose
```
