# Maintainability: Principles

Read this once per session, before the first change. Read the per-property files only when fixing
a finding of that property.

## Priority when guidelines conflict

Lower-level (unit) guidelines take precedence over higher-level ones — [unit-size.md](unit-size.md),
[unit-complexity.md](unit-complexity.md), [duplication.md](duplication.md) and
[unit-interfacing.md](unit-interfacing.md) before [module-coupling.md](module-coupling.md).

## Clean code in the code you touch

Not a measured property — hygiene for the lines a fix touches, so a refactor doesn't trade one
problem for a different mess. Don't clean up the rest of the file: unrelated changes make the diff
harder to review and are not what the candidate asked for.

1. **No unit-level smells** in the units you create or change — see [unit-size.md](unit-size.md),
   [unit-complexity.md](unit-complexity.md), [unit-interfacing.md](unit-interfacing.md).
2. **No bad comments** — an inline comment explaining *what* a block does usually means the block
   should be its own well-named method. Comments explaining *why* are fine.
3. **No code left in comments** — version control has the history.
4. **No dead code** — unreachable branches, unused private methods, results never used.
5. **No overly long identifiers** — a name that packs several responsibilities
   (`generateConsoleAnnotationScriptAndStylesheet`) marks a unit that should be split.
6. **No magic constants** — name unexplained literals (thresholds, rates, limits).
7. **No badly handled exceptions** — never swallow silently, catch the specific type rather than
   a blanket base exception, and don't leak internal exception detail to end users.
