# Unit Size

See also [unit-complexity.md](unit-complexity.md) — the two properties are frequently violated
together and fixed with the same refactorings.

## Guideline

Limit units (methods/constructors) to **15 lines of code** (comments and blank lines excluded).
Short units are easier to test in isolation, easier to analyze, and easier to reuse (long units
bundle several specific responsibilities so they rarely fit a new caller's exact needs).

Risk brackets: ≤15, 16–30, 31–60, >60 LOC. Moving a unit down a bracket (e.g. 80 → 40) is progress
even without reaching ≤15 — see the LOC-weighted scoring and "When to stop" in `SKILL.md`.

## Root cause

A long unit is almost always doing more than one job — e.g. mixing request handling, data access,
business logic, and output formatting in one method. Splitting exposes the seams.

## How to fix it

- **Extract Method** — pull an independent block into its own named method. Works when the block
  doesn't need many local variables passed around and doesn't need to return multiple values. This
  is the default move.
- **Replace Method with Method Object** — when a block uses several local variables and/or the
  parent has multiple exit points, turning the whole method into its own small class (with those
  locals as fields) avoids passing a long parameter list to the extracted method. Use this instead
  of Extract Method when Extract Method would itself create a
  [unit-interfacing.md](unit-interfacing.md) violation.
- If a unit "cannot" be split (e.g. a long `switch`/case block, or a long fluent expression like
  query-builder chaining), check whether the *architecture* is the real problem — e.g. business
  logic and markup construction living in the same method — before accepting the violation.

Splitting increases total line count (a 16-line method split into two units may total 25 lines).
That's expected and acceptable.

## Non-fixes to avoid

Don't comply by cramming multiple statements onto one line or nesting braces to save lines —
that trades unit-size compliance for readability, which is the opposite of the goal.
