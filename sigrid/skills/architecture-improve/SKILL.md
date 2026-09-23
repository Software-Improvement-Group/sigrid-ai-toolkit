---
name: architecture-improve
user-invocable: true
disable-model-invocation: false
description: >
  Makes the structural fix that architecture-diagnose named: moves or splits files, adds a facade,
  reroutes calls, fixes imports, verifies against Sigrid's numbers. Reads the handover doc
  diagnose wrote; with none present it runs architecture-diagnose first. Use for "implement the
  architecture fix", "apply the architecture handover", or after diagnose when the user picks
  "implement it now". Makes code changes. For finding what to fix, use architecture-diagnose.
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/architecture-diagnose/references/graph.md` first: it says
what Sigrid counts and how each mechanism moves each number.

## Input

One handover doc, `.sigrid/architecture-handover-<slug>.md`, written by architecture-diagnose.
Its sections (Goal, System, Evidence, Plan, Done when, Do not, Not covered) are the brief. Work
from the doc; ignore any diagnose output still in the window and do not re-derive the diagnosis.

- The user names one, or exactly one exists: use it.
- Several: ask which.
- None: say "no diagnosis to act on, diagnosing first", invoke `architecture-diagnose`, then
  continue from here with the handover it wrote.

**Goal** and **Done when** are fixed. **Plan** is diagnose's prediction from the graph; you have
the code, so you may change the mechanism when the code shows the plan is wrong, as long as the
result reaches **Done when** and violates nothing in **Do not**. A change of mechanism goes in
the report with the reason.

## Preflight

1. Clean worktree, or ask.
2. Right branch. On the baseline from **System**: branch off it, named per the profile's
   convention. On a branch containing the baseline head: stay. Otherwise ask. Never fetch or pull.
3. Find the build and test commands. None: say so; type-checking is the only net.
4. Read the files in **Evidence** and every caller of what changes. Grep the whole repository;
   large repo: delegate to `explore-codebase`, which has the graph. Count the call sites per
   direction and compare with the baseline numbers in **Evidence**. A big gap is calls Sigrid
   cannot resolve; note both counts and work from the measured ones, since moving unmeasured
   calls moves no rating.
5. **Public surface.** An old path or name referenced from outside the code you control (package
   exports, artifact paths, config or reflection strings, serialized names, plugin registrations)
   keeps working: a forwarding shim at the old location, or the registration updated. Neither
   possible: stop and ask. A shim has no edges, so it does not undo the change.

## Execute

Follow **Plan** in order, or your amended plan. After each step: build green, tests green, one
local commit named after the step. A step still red after one retry: revert to the previous
commit, mark it skipped, continue with the steps that do not depend on it.

Invariants:
- **Behavior-preserving.** Files move, files split along unit boundaries, a facade wraps calls,
  call sites are rerouted or consolidated. Semantics do not change. A step that needs a
  behavior change to be possible: stop and ask.
- **Real edges only.** A facade contains code that calls the target, and callers call the
  facade; a re-export is not a facade. Never replace a direct call with injection, reflection,
  or a string lookup to make it disappear.
- Nothing in **Do not** gets worse.
- No new cross-directory call. A step that forces one goes in the report, not around it.
- Empty diff after **Plan**: the handover was wrong. Stop and ask.

## Verify

Sigrid's tools describe the baseline and cannot see your branch, so you redo its arithmetic.

1. Build and tests on the finished branch.
2. **Numbers.** For the target directory and every neighbor named in **Do not**, count the
   actual call sites crossing each line in the working tree, per direction, as in Preflight 4.
   Compare with **Done when**. Not reached: say which number missed and by how much; do not
   soften the goal to fit.
3. `architecture-drift` on the diff against the baseline: no new cross-directory dependencies,
   no bypassed facade.
4. `guardrails_quality_check` on the changed files.

## Report

What changed and how, where the mechanism differs from **Plan** and why, shims left, steps
skipped and why, the before and after numbers next to **Done when**, what drift and guardrails
said. One closing line: Sigrid re-measures on the baseline, so the structure rating stays
unverified until it re-analyzes; the counts above are the proxy.
