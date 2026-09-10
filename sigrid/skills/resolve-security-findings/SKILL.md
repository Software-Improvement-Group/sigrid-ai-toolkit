---
name: resolve-security-findings
user-invocable: true
description: >
  Triage Sigrid (SAST) security findings — classify each as false positive, risk accepted, or will
  fix then write the decision back to Sigrid and potentially fix the code. Use when the user wants
  to triage security findings, resolve a specific finding, work through a findings backlog, or asks
  "what should I do about this finding", "mark this as a false positive / accepted risk", or "fix
  this Sigrid security finding".
---

# Resolve Security Findings

## Scope

This skill deals with Sigrid security findings:
New finding → Analysis → false positive? → (no) → accept risk? → (no) → blocked? → (no) → fix
(default) → Fixed.

## Prerequisites

- **Sigrid profile** — read `${CLAUDE_PLUGIN_DATA}/CLAUDE.md`, selecting the active system per its
  resolution rule, for `customer` and `system` (required by both MCP tools below) and its "Security
  findings triage" section: the security model is optional (omit the parameter if blank — use
  default).
- Sigrid MCP: `get_finding`, `security_get_findings`, `update_finding_status`,
  `guardrails_quality_check`.

## Entry points

- **A specific finding ID** — call `get_finding` with `finding_type: "security"` to fetch its
  details directly; no need for `security_get_findings`.
- **A pasted finding** (e.g. copied from the Sigrid UI, no UUID) — resolve to a `finding_id` by
  calling `security_get_findings` with `path_prefix`. No match, or more than one match: still
  analyze and (if warranted) fix the code, but skip `update_finding_status` and tell the user
  the finding is ambiguous and status must be updated manually in Sigrid.
- **Bulk / no input given** — call `security_get_findings` with defaults for whatever is not defined
  yet, but pass `status: ["RAW", "REFINED", "WILL_FIX"]` explicitly — the tool's own default also
  includes `ACCEPTED`, which would resurface findings a human already accepted. Include `ACCEPTED`
  only if the user asks to revisit already-accepted findings. Pass `path_prefix` when the user
  scopes the request to an area.

## Modes

Default to **interactive**. Only run **autonomous** when the user explicitly asks for it — never
infer it from being unattended, scripted, or run in a loop.

| Decision point | Interactive | Autonomous |
|---|---|---|
| Classify as false positive / accepted | Propose with evidence, confirm before writing | Propose with evidence, write immediately |
| Commit the fix | Ask once if not stated (default: yes) | Always, one commit per finding |
| Promote a committed fix to `FIXED` | Ask once at the end of the run | Automatic, after the commit |

**Autonomous preflight.** Autonomous mode requires three things in context before Stage 1:

1. **Reachability facts** — what is externally reachable, what is internal-only.
2. **A severity ceiling** — the severity above which nothing is suppressed; those findings go to
   `REFINED` instead. Name the scale when asking: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`. Offer to
   lower it.
3. **Acknowledgement** that the risks accepted this run still need a human to review them afterwards.

If all three are present, proceed stating why. If any is missing, name which ones and get an explicit
"yes, proceed" before continuing.

## Procedure

### Stage 1 — Resolve input

Per the entry-point rules above. If nothing was provided and this is autonomous mode, fetch the
default bulk set — do not ask.

If a finding has toolName "SIG Open Source Health" skip it rather than proceeding.
Autonomous: skip silently. Interactive: tell the user to use the `fix-osh-risk` skill for these instead.

**More than one finding?** Fan out Stages 2–3 (read-only analysis + classification) to one subagent
per finding.

- Cap concurrency at ~8 subagents in flight; queue the rest.
- Brief each subagent with the `finding_id` and the profile's customer/system/security model — don't
  let it re-resolve the profile itself.
- Each subagent returns exactly one thing: the classification and its evidence sentence, the blocker
  that sent it to `REFINED`, or the reason it fell to `WILL_FIX`.
- A subagent that errors or returns nothing: report that finding as unresolved rather than dropping
  it silently.

### Stage 2 — Analyze

Read the flagged code and its surrounding context. This is the step the classification in Stage 3
depends on — don't classify without reading the actual file:line.

### Stage 3 — Classify (evidence gate)

`FALSE_POSITIVE` and `ACCEPTED` each require concrete evidence — a file:line plus one sentence —
or the finding falls through to the two outcomes below. Every gate here is mechanical — a named
trigger, never a confidence score.

- **False positive**: the check itself is wrong, not the code — like steam triggering a smoke
  detector. The tell: the best fix would be to fix the check, not the flagged code. If the fix 
  you'd reach for is a code change, it isn't a false positive.
- **Accepted risk**: real issue, but the residual risk is acceptable *at Sigrid's original
  severity* — name the mitigating context (e.g. "internal-only admin endpoint, no external route,
  see `routes.py:80`"). No severity override exists to lean on here.
- **Needs human review** (`REFINED`): no evidence for either of the above, *and* any one of these
  holds — the fix requires a design or product decision rather than a mechanical change; it would
  change the auth/access-control decision itself rather than harden it; remediation needs an action
  outside the working tree (secret rotation, infra or config change, dependency bump); Stage 2 could
  not locate the sink or data flow the finding describes; the fix would change an exported signature
  or need edits in more than 3 files. Name the blocker in one sentence, skip Stage 5, and do not
  suppress.
- **Will fix** (the default): no evidence for false positive / accepted, and no blocker above.

Stage 4's remark is this evidence sentence or blocker, verbatim or lightly cleaned up — don't write
it twice in different words.

### Stage 4 — Write back to Sigrid

Do this before touching any code, so an interrupted run still leaves the triage decision recorded.
Call `update_finding_status` with:
- `status`: `FALSE_POSITIVE`, `ACCEPTED`, `REFINED`, or `WILL_FIX`. `FIXED` is only set in Stage 6,
  once the fix is committed.
- `remark`: the Stage 3 evidence sentence (false positive / accepted), the named blocker
  (`REFINED`), or the fix you are about to make in one sentence (will fix). Prefixed with
  "Sigrid Auto-fix Agent:".

Skip this call entirely if Stage 1 couldn't resolve a `finding_id` (ambiguous pasted finding) —
report that to the user instead.

### Stage 5 — Fix (will-fix path only)

1. Write the code fix directly in the working tree, following the finding's recommendation.
2. Run `guardrails_quality_check` on the changed code snippet(s) — it takes code, not a path,
   Only the security-category results matter (ignore maintainability); fix anything new it flags
   before moving on.
3. Commit:
   - Autonomous: one commit per finding, message `Fix: <finding title> (Sigrid <finding_id>)`.
   - Interactive: ask once per run whether to commit at all (default: yes); if yes, same
     one-commit-per-finding convention.

### Stage 6 — Promote to `FIXED`

Once at the end of the run, for the findings whose fix was actually committed in Stage 5, call
`update_finding_status` again with `FIXED`.

- Interactive: list them and ask — set them to `FIXED` now, or leave them on `WILL_FIX` until the code
  is merged? Both are fine.
- Autonomous: do it without asking to ensure these findings are not retrieved in later runs.

Then state in the report which findings are now `FIXED`, and that if those commits do not get merged
they must be set back to `WILL_FIX`.

### Stage 7 — Report

Always close by listing in chat every finding that landed on `REFINED` — finding ID, file:line, and
the blocker — plus any finding a subagent failed to resolve. Required in both modes: nobody is
looking at Sigrid at the end of this run.