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

Executes refactoring candidates identified by Sigrid. Two modes: autonomous (runs the primary finding and runner-ups from sigrid-diagnose, you review diffs at the end) or interactive (you steer priorities and provide context, one step at a time). Read + Write. Code changes ARE made.

## References

Read these on the following triggers — nothing else:

- **Once per session, before the first change:** [principles.md](references/principles.md) — priority when guidelines conflict, and clean-code hygiene for the code you touch.
- **When creating or editing tests:** [testing.md](references/testing.md).
- **Only when fixing a finding of that property** (in Step 3, before touching code) — the guideline, root cause, refactoring techniques, and bracket edges:
  - [unit-size.md](references/unit-size.md) — long methods/constructors (>15 LOC)
  - [unit-complexity.md](references/unit-complexity.md) — high branching (McCabe >5)
  - [duplication.md](references/duplication.md) — copy-pasted code (6+ identical lines)
  - [unit-interfacing.md](references/unit-interfacing.md) — long parameter lists (>4 params)
  - [module-coupling.md](references/module-coupling.md) — large, high-fan-in classes

## Prerequisites

- Sigrid customer and system come from the Sigrid profile written by `/sigrid:setup` at `${CLAUDE_PLUGIN_DATA}/CLAUDE.md`. The profile may list several systems; select the one whose `Repo` key matches the current repository, per the profile's resolution rule. Apply any behavior guidance the profile records (e.g. off-limits code, preferred levers). If the profile is missing, no entry matches, or the match is ambiguous: in **interactive** mode, ask the user (and suggest running `/sigrid:setup`); in **autonomous** mode, abort with a clear error. Whenever any profile-covered setting is established during the run by asking or stated inline (customer/system, baseline branch, behavior preferences, or any other), write it back into the profile additively (keyed by the current repo's remote where system-specific) so future runs resolve without asking.
- The Sigrid MCP tool `guardrails_quality_check` is available. If not available: abort with a clear error regardless of mode.

## Autonomy modes

**Interactive** — asks at each decision point. If a prerequisite is missing, ask the user to resolve it.

**Autonomous** — follows defaults, never blocks. When blocked, skips and logs rather than asking. If a prerequisite is missing, abort with a clear error.

| Decision point                                                                                   | Interactive                          | Autonomous                                             |
|--------------------------------------------------------------------------------------------------|--------------------------------------|--------------------------------------------------------|
| Which candidates to act on                                                                       | User confirms or selects from list   | Primary finding + runner-ups from sigrid-diagnose      |
| Missing context before a candidate (serialization constraints, known callers, migration windows) | Ask the developer                    | Skip and log as "skipped — missing context"            |
| Guardrail failure that cannot be resolved                                                        | Ask: try different approach or skip? | Revert, log as "skipped — guardrail failure", continue |
| Build or type error after refactor                                                               | Ask: try different approach or skip? | Revert, log as "skipped — build error", continue       |
| Tests fail after refactor                                                                        | Ask: try different approach or skip? | Revert, log as "skipped — tests fail", continue        |

## How to run

### Step 1 — Establish context

If invoked right after `/sigrid:sigrid-diagnose` in the same session, reuse its output directly: you already know the primary finding, any runner-ups, and the rejected candidates (do not re-propose a candidate sigrid-diagnose already rejected — treat its reject-rule notes as binding).

If no diagnosis is in context (fresh session), look for a handover doc at `.sigrid/maintainability-handover.md`. If present, read it — it contains the primary finding, runner-ups, candidate IDs/file paths, and reject-rule notes exactly as sigrid-diagnose presented them. Treat it as authoritative and do not re-derive or second-guess its reject decisions.

If neither is available, run `/sigrid:sigrid-diagnose` first.

### Step 2 — Ask for mode (if not already provided)

Present the two options concisely:

    Two modes available:
      autonomous  — executes the primary finding and any runner-ups from sigrid-diagnose, you review diffs at the end
      interactive — together we decide what to tackle and in what order, I'll ask for context where needed

    Which mode? [autonomous / interactive]

**Autonomous mode:** use the primary finding plus runner-ups from sigrid-diagnose's output (skip anything it listed under "Rejected candidates") and proceed without further approval. Never block — see decision-point table above.

**Interactive mode:** present the primary finding and runner-ups with a brief rationale for each (property, LOC at risk, and whether it is a simple extraction or a cross-cutting concern). Ask the developer which to prioritise and whether to skip any. For each candidate, ask for missing context before starting. After each change, show the diff and ask `Continue to next candidate? [yes / skip / stop]` before proceeding.

### Step 3 — For each candidate, execute the refactoring

**Read the file.** Understand the full class before touching anything.

**Run the existing tests that cover it** before the change, so a failure afterwards is known to be
yours. If nothing covers the code, add a test for the behavior you are about to move (see
[testing.md](references/testing.md)).

The metric value (LOC, McCabe, parameter count, fan-in, clone size, ...) comes from the candidate
data sigrid-diagnose already retrieved via `maintainability_get_findings` — never re-derive or hand-count it
from the source. Read the matching reference file above for *how* to fix a finding of this
property; the *whether-it's-still-a-violation* question is answered by the tool data going in and
by `guardrails_quality_check` (Step 4) coming out.

Scoring is LOC-weighted: a finding's impact = its LOC in a risk bracket / total system LOC. A valid fix is anything that reduces LOC carrying bad-bracket risk — either by crossing a bracket edge (change the metric value) or by reducing the unit's/module's LOC so it weighs less in its current bracket. Pick whichever the code structure supports.

Look at the actual finding — the specific code, the violation magnitude, the surrounding context — and reason about the right fix.

### When to stop

A refactoring is **done** when:
- Guardrails pass with no new findings introduced.
- The tests that passed before still pass.
- The metric improved — the candidate is no longer a top offender.
- All call sites still compile and the code is readable.

Do not refactor for a perfect score. If the improvement is close enough (e.g. method went from 40 lines to 17), move on.

### Step 4 — Run tests and guardrails after each change

Run the tests from Step 3 again. Then run `guardrails_quality_check` on each changed file (it
takes the file's full contents and filename, not a path or a diff).

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

- Never change an external interface: public API signatures, serialized field names, or any other wire contract that callers outside the repo depend on. sigrid-diagnose rejects candidates that need this; if a fix turns out to need it anyway, skip the candidate.
- Component-level properties (componentIndependence, componentEntanglement): do NOT make code changes. sigrid-diagnose only passes these on when nothing else qualified; surface the issue and point the developer to `/sigrid:architecture-diagnose`.
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
- `guardrails_quality_check` tool unavailable or returns an error: note the failure, treat guardrails as unknown (⚠ unverified) in the report, continue — do not block on a tool outage.
- Call sites in generated or external code that cannot be updated: note which call sites were left unchanged and warn that the refactoring may require a manual follow-up.
- Empty candidate list from sigrid-diagnose: report "No candidates found — nothing to do" and stop.
- `.sigrid/maintainability-handover.md` missing, unreadable, or naming a different customer/system than the current profile: do not guess its contents — run `/sigrid:sigrid-diagnose` first instead.
- Candidate is component-level: see Invariants above.
