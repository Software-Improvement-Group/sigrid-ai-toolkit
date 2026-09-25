---
name: sigrid-diagnose
user-invocable: true
description: >
  Finds the highest-leverage maintainability problem in a Sigrid system — the property most worth
  fixing and the concrete candidates that drive it — or reports that nothing qualifies. Diagnoses
  only; code changes are handed off to sigrid-improve. Use for "why is our maintainability rating
  low", "where should we improve code quality", "diagnose maintainability of <system>". For
  architecture-level structure (coupling, cohesion, component boundaries), use
  architecture-diagnose instead.
---

# Sigrid Diagnose

## Goal

Diagnosis only: identify where maintainability can be improved and why, judge whether each
candidate is really worth fixing, then stop before implementation. That belongs to
`sigrid-improve`, which this skill hands off to.

Not all refactoring candidates are equal. Choosing the wrong one wastes effort on low-impact or
high-risk changes. This skill's job is to reject the noise so `sigrid-improve` only ever sees
high-leverage candidates.

## Prerequisites

- Sigrid customer and system come from the Sigrid profile written by `/sigrid:setup` at
  `${CLAUDE_PLUGIN_DATA}/CLAUDE.md`. The profile may list several systems; select the one whose
  `Repo` key matches the current repository, per the profile's resolution rule. If the profile is
  missing, no entry matches, or the match is ambiguous, ask the user (and suggest running
  `/sigrid:setup` to persist them). Whenever any profile-covered setting is established during the
  run by asking or stated inline (customer/system, baseline branch, or any other), write it back
  into the profile additively (keyed by the current repo's remote where system-specific) so future
  runs resolve without asking.
- The Sigrid MCP tools `maintainability_get_ratings` and `maintainability_get_findings` are
  available. They describe Sigrid's last baseline analysis, never the working tree.

### Tool gotchas

- `maintainability_get_findings` with `count=100` on a large system can exceed the tool-output
  token limit — the result silently gets written to a scratch file instead of returned inline, and
  you must read it back in chunks. Check for the truncation notice rather than assuming the result
  is inline.
- `status` on each candidate can be `RAW`, `WILL_FIX`, or `ACCEPTED`. `ACCEPTED` means the team has
  already triaged and deprioritized it — exclude these (see reject rules).

## How to think about maintainability

There is no fixed checklist; reason from the numbers and the code. A property's low score always
traces to one of two shapes:

1. **A concentrated cluster** — a handful of files/units carry a disproportionate share of the
   bad-bracket LOC (e.g. five DTOs with 20+ parameter constructors). *Fix:* touch those specific
   files; the fix is contained and high-leverage because a small number of changes move a
   meaningful share of the score.
2. **A diffuse spread** — the bad-bracket LOC is spread thinly across many unrelated files, none
   individually dominant. *Fix:* usually not worth chasing file-by-file; look for whether a single
   structural cause (a shared base class, a code-gen template, a copy-pasted pattern) explains the
   spread — if one exists, fixing the cause fixes many findings at once. If no shared cause exists,
   say so and treat the property as low-leverage regardless of its star rating.

A property's rating changes in exactly two ways: a finding's metric value crosses a bracket edge
(e.g. params 8 → 4), or the LOC carrying the bad-bracket weight shrinks (e.g. a large unit is
split so each half weighs less). Both are legitimate; pick whichever the code structure supports.

## How to determine which refactoring candidates have the most impact

### 1. Retrieve maintainability ratings

Use `maintainability_get_ratings`. Parse the result: unitSize, unitComplexity, unitInterfacing,
duplication, moduleCoupling, componentIndependence, componentEntanglement — each 0.5–5.5 stars.
Sort worst-first and compute the gap to 4.0 for each.

### 2. Get refactoring candidates for ALL properties

Call `maintainability_get_findings` with `count=100` for every property in parallel. Do not limit
to the weakest property only — cross-referencing across all properties is essential (see step 3).

### 3. Choose the most impactful refactoring candidates

#### 3a. Cross-reference findings across properties

A finding that appears in multiple property lists is a higher-leverage target than one that
affects only a single metric. For each candidate, note which properties it contributes to.
Prioritise findings that show up in 2+ lists.

#### 3b. General considerations

- Is the pattern a concentrated cluster or a diffuse spread (see "How to think about
  maintainability")? A single finding does not move a system rating much.
- Judge candidates against best practices for that language.

`componentIndependence` and `componentEntanglement` are component-level and `sigrid-improve` does
not change them. Only pick one when no other property has a qualifying candidate; then present it
as a suggestion and point to `/sigrid:architecture-diagnose`, which has the graph tools to diagnose
it properly.

`maintainability_get_findings` results are already sorted by LOC-weighted contribution, so the
first results per property are the highest-impact ones for that property.

### 3c. Targets and reject rules

- A property only qualifies for the action plan if its gap to 4.0 is meaningful. Do not build a
  plan around a property that is within ~0.1 stars of 4.0 with no concentrated cluster behind it —
  say it's not worth chasing right now instead of forcing a finding.
- Reject a candidate, and say which rule applied, when it is:
  - generated, vendored, or test code;
  - status `ACCEPTED` (already triaged and deprioritized; `WILL_FIX` may still be included);
  - only fixable by a change that would visibly worsen a different property or file (e.g. splitting
    a unit in a way that increases duplication elsewhere) — note the trade-off instead of silently
    picking a side;
  - only fixable by changing an external interface: a public API signature, a serialized field
    name, or another wire contract that callers outside the repo depend on. A public unit whose fix
    stays internal (e.g. splitting a long endpoint body) still qualifies.
- If, after reject rules, no candidate survives for the weakest property, fall back to the
  next-weakest property that still has a qualifying candidate. If none has, say so plainly (see
  Output) and stop — do not force a plan.

## Verification

Before finalizing the action plan: for each candidate you intend to report, confirm you actually
read the file (or, for component-level properties without a single file, the component names)
and that the LOC/status fields you're citing came from the tool response, not inferred. If a
flagged file no longer exists at that path (renamed, moved, deleted since the last Sigrid
snapshot), say so and drop it rather than reporting stale data as current.

## Output

State findings as problem/solution pairs, ELI5, in a few sentences each: what is wrong and what a
fix looks like. Talk about the code, not the tools or metrics used to find it — someone who works
in the repo should think "yes, I recognize that." Ground every claim in something read from the
actual file (see Verification); never describe a hotspot using only metric language (property
names, star ratings, severity) with no concrete detail.

One primary finding, with runner-ups if any survive the reject rules. Structure:

Ratings at a Glance

    <property>    <rating>    <gap to 4.0>
    ... (all 7 properties, sorted worst-first)

Primary Finding

    Problem: [what's structurally wrong, grounded in the actual file content]
    Solution: [what fixes it, in one or two sentences — no implementation detail, that's sigrid-improve's job]
    Properties affected: [list — call out if 2+, that's why it's primary]

Runner-ups (if any)

    Same problem/solution shape, briefer.

Rejected candidates (only if something notable was excluded)

    One line each: candidate, rule that removed it.

Do not include projected rating improvements anywhere in the output (Sigrid does not expose
projected score deltas) — describe impact qualitatively only (e.g. "removes the largest single
source of duplication").

If nothing qualifies across all seven properties, say so in one sentence per property considered,
naming the rule that removed its best candidate, and do not proceed to the next-step question
below.

## Next step

Otherwise, ask (`AskUserQuestion`) whether to: implement it now, implement it in a fresh session,
write a handover doc for another agent, or just talk it through first.

For every option except "talk", write a handover doc to `.sigrid/maintainability-handover.md`
first — this is the brief `sigrid-improve` works from, since chat history is not a reliable
handoff. It contains:

- Sigrid customer and system, and today's date;
- primary finding + runner-ups exactly as presented, with candidate IDs and file paths;
- the rejected candidates and the rule that removed each.

It is a working file: do not commit it. Then:

- **fresh session** (recommend when this run was long): tell the user to `/clear` and run
  `/sigrid:sigrid-improve`; it finds the handover in `.sigrid/` by itself.
- **handover for another agent**: give the path and stop.
- **now**: invoke `sigrid-improve` with the candidates just diagnosed. Say in one line that the
  diagnose context stays in the window.
