# Handover doc

This is the brief architecture-diagnose writes for architecture-improve. The reader is a capable
agent with zero context that cannot ask you anything: it will read the code, choose how to make
the change, and check its own work against the numbers you give it. Spell out paths, files, and
directions; never "as discussed" or "the directory above". The section names and order below are
fixed; improve looks them up by name.

Write to `.sigrid/architecture-handover-<slug>.md`, `<slug>` being the target's local path with
slashes turned into hyphens. Create `.sigrid/` if missing; if the file exists, ask before
overwriting.

Use only what this run produced — tools, describers, source you read. Write
`unknown` rather than a plausible value. Numbers are what let the reader verify; a section
without them is an opinion.

Sections, in order:

1. **Goal** — two sentences, imperative, naming local paths: what should be true of the target
   directory afterwards, and which sub-metric that fixes.
2. **System** — Sigrid customer and system, the target's Sigrid and local path, baseline branch.
3. **Evidence** — verdict (`breakdown` / `boundary` / `enforcement`), structure rating, failing
   sub-rating with its rating, and what the graph and describers showed: the responsibility
   groups with their members, the loose root files, or the neighbor the calls all run to. Then
   the baseline numbers per file involved: calls with the destination, with current siblings,
   elsewhere, from `architecture_get_external_dependencies`. Note edges you expect the graph to
   be missing and whether the source confirmed them.
4. **Plan** — the fix you predicted, as numbered steps, each with the expected effect on the
   numbers above. Mechanisms: move, split, facade with real calls, reroute or consolidate call
   sites, per `graph.md`. Full paths, and for a split the units that leave. The reader may
   choose a different mechanism if the code makes yours wrong; it must reach the same numbers.
   Every step must be executable as written — no conditional branches, no "if X then Y else Z",
   no "decide between A or B". If you cannot commit to a step, the finding is not ready to hand
   over; diagnose further or drop it.
5. **Done when** — the target's numbers after the change (`cohesion above 70% internal`,
   `at most 3 files in the target with external edges`). Never predict a star-rating delta;
   Sigrid does not expose projected scores.
6. **Do not** — the sibling, parent, or destination that must not get worse and what would push
   it there; fixes the reject rules excluded that a reader might try next.
7. **Not covered** — the sub-metrics this fix does not touch.

Then one sentence in the chat: the path written and the one-line goal.
