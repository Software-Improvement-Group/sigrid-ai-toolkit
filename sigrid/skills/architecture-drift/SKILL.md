---
name: architecture-drift
user-invocable: true
disable-model-invocation: false
description: >
  Flags architecture drift introduced by an in-progress change (a git diff, staged
  change, or feature branch) by grounding it in Sigrid's architecture graph.
  Detects new cross-directory dependencies, bypassed boundary/facade modules, new
  circular dependencies, and risky blast radius from contract changes — then
  recommends specific files to touch instead. Works at any level of granularity —
  file, directory, or subsystem. Use before committing or opening a PR,
  or whenever the user asks "does this change introduce bad coupling",
  "check my diff/PR for architecture drift", "will this break our module boundaries",
  "did I bypass the gateway/facade", "is this new dependency safe", or "what depends on this file".
  This is a lightweight, diff-scoped check grounded in real Sigrid dependency data,
  not code-reading heuristics. For a full system-wide architecture
  audit (coupling/cohesion toplists), use a heavier workflow instead.
---

## Core Idea

Use this before committing or opening a PR, or when reviewing someone else's
branch for architecture risk before merging.

- **The diff is the source of truth for what's new.**
- **The Sigrid architecture graph is the source of truth for what already exists.**

A new reference that matches an edge that already exists is normal evolution —
nothing to flag.

**A new reference that doesn't match anything in the graph, or that
closes a cycle, or that skips an existing high-traffic gateway file, is a drift
signal.**

## Prerequisites

- Sigrid customer and system come from the Sigrid profile written by `/sigrid:setup`
  at `${CLAUDE_PLUGIN_DATA}/CLAUDE.md`. The profile may list several systems; select
  the one whose `Repo` key matches the current repository, per the profile's
  resolution rule. If the profile is missing, no entry matches, or the match is
  ambiguous, ask the user (and suggest running `/sigrid:setup` to persist them).
  Whenever any profile-covered setting is established during the run by asking or
  stated inline (customer/system, baseline branch, or any other), write it back into
  the profile additively (keyed by the current repo's remote where system-specific)
  so future runs resolve without asking.
- Sigrid MCP available: `architecture:get_internal`, `architecture:get_external_dependencies`

  | MCP tool | Purpose |
  |---|---|
  | `architecture:get_external_dependencies` | Incoming callers of a touched file — blast radius if its contract changes |
  | `architecture:get_internal` | Current dependency structure anchored on the touched files/directories |

  If either tool is unavailable, state which one and stop. Don't approximate the
  dependency structure from reading code — the differentiator is Sigrid's measured
  graph.

## Step 1 — Read the Diff

Read the added lines (`git diff`) to find new imports, calls, instantiations, and type references that
may cross into another directory or module — this applies at any level, from sibling files up to whole subsystems.

## Step 2 — Ground: Current Dependency Structure

To get the current structure, call:

```
architecture:get_external_dependencies(customer, system,
    path=<one touched file path or its common parent directory>, direction="all")
```

`path` takes a single string prefix, not a list. If several files in the same
group changed, call once per file, or once on their common parent directory if
they share one — either way you get edges to/from exactly the files that changed.
One call per distinct group.

**Constraint: maximum of ~5 distinct top-level directories** - the diff itself may be too broad for one pass.
Prioritize the groups with the most touched files or the most new external
references found in Step 1, run the check on those, and explicitly report which
directories were skipped so the user can rerun the skill scoped to them.

## Step 3 — Cross-Reference: Is This Reference Consistent With the Architecture Graph?

For each new reference found in the diff, check it against the *current* measured structure:
does an edge already exist between these two directories? In which direction? Through which files?

## Step 4 — Output

Report whether something needs to change.
If yes, indicate what and why. If not, state it clearly to the user.
