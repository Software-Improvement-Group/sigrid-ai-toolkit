# Duplication

## Guideline

Never copy-paste code. SIG counts a duplicate ("Type 1 clone") as an *identical* sequence of **6+
lines of code** (ignoring whitespace/comments), regardless of whether it spans method or class
boundaries. Short 3–4 line patterns repeated across domain objects are below this threshold and not
the target.

A duplicate means a bug fix or behavior change must be made in every copy, and missing one copy is
a classic source of regressions.

## How to fix it

- **Extract Method** (see [unit-size.md](unit-size.md)) when the duplicate is within one class or
  can be lifted to a shared home. Put it in a class that is naturally responsible for that logic —
  dumping it into an unrelated utility class just to have a home recreates the large-class problem
  from [module-coupling.md](module-coupling.md).
- **Extract Superclass** (or a shared base/mixin, per the language) when the duplicate spans two
  related classes (e.g. two account types sharing validation logic): move the shared logic up so
  each subclass adds only what's specific to it.
- Shrinking a clone below 6 lines makes it "solved" per the metric while the same *logic* still
  lives in two places — extract it fully instead.
- Long string literals (SQL, HTML/XML built via concatenation) that repeat except for small
  variations are not exempt — extract into a parameterized method, or use a templating engine for
  markup.
