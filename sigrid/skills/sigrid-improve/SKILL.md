---
name: sigrid-improve
user-invocable: true
description: >
  Use when the user wants to act on a Sigrid maintainability diagnosis — fix refactoring candidates,
  reduce a low-rated property, or apply improvements surfaced by sigrid-diagnose. Trigger on phrases
  like "fix this", "apply these improvements", "start refactoring", "work on the candidates", or any
  request to make code changes based on Sigrid findings. Makes actual code changes. Run after
  sigrid-diagnose, or run sigrid-diagnose first if no diagnosis is in context yet.
---

# Sigrid Improve

Executes refactoring candidates identified by Sigrid. Two modes: autonomous (runs all candidates from sigrid-diagnose, you review diffs at the end) or interactive (you steer priorities and provide context, one step at a time). Read + Write. Code changes ARE made.

## Prerequisites

- Sigrid customer and system name come from the Sigrid profile written by `/sigrid:setup` at `~/.claude/plugins/config/sigrid-ai-toolkit/sigrid/CLAUDE.md`. Apply any behavior guidance the profile records (e.g. off-limits code, preferred levers). If the profile is missing or the values are unset: in **interactive** mode, ask the user (and suggest running `/sigrid:setup`); in **autonomous** mode, abort with a clear error.
- The Sigrid MCP plugin is available: `code_quality_guardrails`. If not available: abort with a clear error regardless of mode.

## Autonomy modes

**Interactive** — asks at each decision point. If a prerequisite is missing, ask the user to resolve it.

**Autonomous** — follows defaults, never blocks. When blocked, skips and logs rather than asking. If a prerequisite is missing, abort with a clear error.

| Decision point                                                                                   | Interactive                          | Autonomous                                             |
|--------------------------------------------------------------------------------------------------|--------------------------------------|--------------------------------------------------------|
| Which candidates to act on                                                                       | User confirms or selects from list   | All candidates from sigrid-diagnose                    |
| Missing context before a candidate (serialization constraints, known callers, migration windows) | Ask the developer                    | Skip and log as "skipped — missing context"            |
| Guardrail failure that cannot be resolved                                                        | Ask: try different approach or skip? | Revert, log as "skipped — guardrail failure", continue |
| Build or type error after refactor                                                               | Ask: try different approach or skip? | Revert, log as "skipped — build error", continue       |

## How to run

### Step 1 — Establish context

If invoked right after `/sigrid:sigrid-diagnose`, reuse its output: you already know the weakest property and the top candidates. If no diagnosis is in context, run `/sigrid:sigrid-diagnose` first.

### Step 2 — Ask for mode (if not already provided)

Present the two options concisely:

    Two modes available:
      autonomous  — executes all top candidates from sigrid-diagnose, you review diffs at the end
      interactive — together we decide what to tackle and in what order, I'll ask for context where needed

    Which mode? [autonomous / interactive]

**Autonomous mode:** use the candidate list from sigrid-diagnose output and proceed without further approval. Never block — see decision-point table above.

**Interactive mode:** present the candidate list with a brief rationale for each (property, LOC at risk, and whether it is a simple extraction or a cross-cutting concern). Ask the developer which to prioritise and whether to skip any. For each candidate, ask for missing context before starting. After each change, show the diff and ask `Continue to next candidate? [yes / skip / stop]` before proceeding.

### Step 3 — For each candidate, execute the refactoring

**Read the file.** Understand the full class before touching anything.

Scoring is LOC-weighted: a finding's impact = its LOC in a risk bracket / total system LOC. A valid fix is anything that reduces LOC carrying bad-bracket risk — either by crossing a bracket edge (change the metric value) or by reducing the unit's/module's LOC so it weighs less in its current bracket. Pick whichever the code structure supports.

Look at the actual finding — the specific code, the violation magnitude, the surrounding context — and reason about the right fix.

### When to stop

A refactoring is **done** when:
- Guardrails pass with no new findings introduced.
- The metric improved — the candidate is no longer a top offender.
- All call sites still compile and the code is readable.

Do not refactor for a perfect score. If the improvement is close enough (e.g. method went from 40 lines to 17), move on.

### Step 4 — Run guardrails after each change

Run `code_quality_guardrails` on the changed file.

- Guardrails pass with no new findings: report "✓ guardrails clean".
- Guardrails surface NEW findings (not pre-existing): fix them before reporting the change done.
- Guardrails surface only pre-existing findings: note them but do not block progress.

### Step 5 — Present results

**Autonomous mode** — consolidated report at the end:

    Refactoring complete — <N> files changed, <M> skipped (error handling)

    ┌───┬────────────────┬────────────┬────────────┬─────────────────────────────────┐
    │ # │ File           │ Before     │ After      │ Status                          │
    ├───┼────────────────┼────────────┼────────────┼─────────────────────────────────┤
    │ 1 │ OrderService   │ 18 params  │ 3 groups   │ ✓ guardrails clean              │
    │ 2 │ ReportConfig   │ 12 params  │ 2 groups   │ ✓ guardrails clean              │
    │ 3 │ PaymentService │ —          │ —          │ skipped — guardrail failure     │
    │ 4 │ UserMapper     │ —          │ —          │ skipped — build error           │
    └───┴────────────────┴────────────┴────────────┴─────────────────────────────────┘

    Run `git diff` to review all changes. Run `git checkout <file>` to revert individual files.

**Interactive mode** — after each file:

    Changed: <file>:<startLine>–<endLine>
    Property: unitInterfacing  |  Before: 30 params  |  After: 3 groups
    Guardrails: ✓ clean  (or: ⚠ N new findings — fixed)

    Diff:
    <show the relevant diff>

    Continue to next candidate? [yes / skip / stop]

At the end of an interactive session, always show a one-line summary:

    Done — <N> changed, <M> skipped (error handling), <K> skipped by user.

## Invariants — never violate these

- Never change the signature of public API endpoints in a way that breaks callers — parameter grouping must be transparent to API consumers (e.g. via serialization annotations).
- Never rename fields or properties that are part of a serialized API contract — that is a breaking change. Use serialization annotations to preserve the wire name if needed.
- Architecture-level properties (moduleCoupling, componentIndependence, componentEntanglement): do NOT make code changes. Surface the issue, explain the impact, and propose a restructuring plan for the developer to decide on.
- Run the project's formatter/linter on changed files before reporting done — formatting is typically enforced by CI.
- After changing a type or function signature, verify all call sites still compile or pass type-checking.

## Call-site update rule

When a function or type signature changes, update all call sites in the same change.

1. Search the codebase for usages of the changed symbol (constructor calls, factory functions, instantiations).
2. Update every call site before reporting the refactoring done.

## Error handling

- File not found: skip the candidate, continue, note in the final report.
- Build or type error after refactor: try resolving it first; if that fails, revert the change and handle per mode (see decision-point table).
- No metric improvement after a valid refactoring (guardrails pass but candidate is still a top offender): try one alternative approach; if it still doesn't move, revert, note as "no measurable improvement", move on.
- `code_quality_guardrails` tool unavailable or returns an error: note the failure, treat guardrails as unknown (⚠ unverified) in the report, continue — do not block on a tool outage.
- Call sites in generated or external code that cannot be updated: note which call sites were left unchanged and warn that the refactoring may require a manual follow-up.
- Empty candidate list from sigrid-diagnose: report "No candidates found — nothing to do" and stop.
- Candidate is architecture-level: see Invariants above.
