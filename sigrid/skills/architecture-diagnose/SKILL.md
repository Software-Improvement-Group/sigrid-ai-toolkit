---
name: architecture-diagnose
user-invocable: true
disable-model-invocation: false
description: >
  Finds the one directory in a Sigrid system whose structure is most worth fixing and names the
  concrete fix, or reports that nothing qualifies. Diagnoses first and asks before changing
  anything. Use for "why is our architecture rating low", "where should we improve our
  architecture", "diagnose the architecture of <directory>". For whether an in-progress diff
  introduces bad coupling, use architecture-drift.
---

Read `references/graph.md` first — it defines what Sigrid measures and how each change moves each
number.

## How to think about architecture

A directory is a module boundary. Use the tools and principles below to find the worst directory
and diagnose *why* its structure is bad. There is no fixed checklist; reason from the numbers and
the code. **Fix boundaries before enforcing them** — when boundaries are wrong, fixing coupling
just moves the hub around.

A good boundary has two properties. When one breaks, it looks like this:

1. **Cohesion** — the files inside form one connected cluster of related work and call each other
   more than they call outside. The graph's cohesion % and `architecture_get_internal` tell you
   this directly; an `explore-codebase` describer confirms what each child does.
   *Broken:* low cohesion, or disconnected clusters in `get_internal` — the directory contains
   two unrelated things, or a child belongs in a neighbor. Fix is structural: split, merge, or
   move children. Dependency cycles (bidirectional edges) are a signal the boundary between two
   children is wrong; which is a pointer to a boundary fix.

2. **Information hiding** — external callers reach the directory through a small surface, not
   scattered across its internals. Centralization measures this as % of LOC in files with no
   external edge — low centralization means too much of the directory's code is directly exposed.
   *Broken:* many internal files have external callers. A facade or gateway consolidates the
   surface.

Also common: **loose root files** (breakdown) — files sitting at a directory's root when
subdirectories exist. They belong somewhere; figure out where from calls and responsibility.
**Excessive coupling** (high edge count or adjacency to many neighbors) — but only after
confirming the boundary itself is right.

A directory's rating changes in exactly two ways: files change directory, or calls change. The
mechanism (move, split, facade, reroute call sites) follows from which property is broken and the
numbers in `graph.md`. Use the ratings as a sanity check, not the goal.

## Tools

Resolve customer, system, and baseline branch from `${CLAUDE_PLUGIN_DATA}/CLAUDE.md` by git
remote. Tools describe Sigrid's last baseline analysis, never the working tree. Read source where
the graph is silent and the answer decides the fix — a missing edge is unmeasured, not absent.

Gotchas:
- `architecture_get_worst_directories`: default `min_volume` (0.2 py) hides leaf dirs on small
  systems — lower to 0.01. Sigrid paths can differ from local layout; check `example_paths` if a
  path returns nothing.
- `architecture_get_internal`: names are bare — resolve to full paths before comparing across
  results.
- `architecture_get_external_dependencies`: capped at 50. If `truncated`, query per child —
  arithmetic on a capped list is wrong.
- `explore-codebase`: describe what each child does, don't judge.

## Targets and reject rules

- Ratings run 0.5 to 5.5 stars. Judge a directory on its **structure** rating; the five
  sub-ratings say *what* to fix, never *whether*.
- Candidate below **3.5**. Between 3.5 and 4.0 only if nothing below 3.5 survives. Never at 4.0
  or above.
- Reject, and say which rule applied, when the directory is:
  - generated, vendored, or test code;
  - only fixable by visibly worsening a sibling, parent, or destination
- A utility-role directory (`null` coupling and adjacency) is not scored on coupling, so never
  propose cutting its dependencies. It can still have loose root files, a wrong boundary, or
  scattered call sites.
- A directory that acts as a helper or utility but isn't auto-detected as one (see
  `references/graph.md`) can be marked in the scope file — read `references/scope-file.md`.
  A helper has no outgoing dependencies to its callers.
- Pick the directory that owns the problem: a parent whose rating is just the aggregate of its
  children is not the target — its children are. A parent whose children are individually at
  target but whose own rating is low is the target.

## Verification

Before proposing a fix, confirm the edges you rely on exist in the tool output and the change
doesn't worsen a neighbor (pushing a sibling, parent, or destination below target).

## Output

State each finding as a problem/solution pair, ELI5, in a few sentences: what is wrong with the
architecture, and what fixes it. Talk about the architecture of the code, not the tools, metrics,
or process used to find it. Someone who works in the repo should think "yes, I recognize that."
One primary finding, some runner-ups if found. No code changes.

If nothing qualifies, say so in one sentence per candidate considered, naming the rule or
objection that removed it, and do not ask the question below.

Otherwise, ask (`AskUserQuestion`) whether to implement it now, implement it in a fresh session,
write a handover doc for another agent, or just talk it through first.

For every option except "talk", read and follow `references/handover.md` first; the doc is the
brief `architecture-improve` works from, so it is written even in the same session. Chat history
is not the handoff. Then:
- *fresh session* (recommend it when this run was long): tell the user to `/clear` and run
  `/sigrid:architecture-improve`; it finds the handover in `.sigrid/` by itself.
- *now*: invoke `architecture-improve` with the path just written. Say in one line that the
  diagnose context stays in the window.
