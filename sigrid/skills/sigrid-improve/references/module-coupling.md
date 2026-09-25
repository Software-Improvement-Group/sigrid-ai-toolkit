# Module Coupling

## Guideline

Avoid large classes in order to keep coupling loose: assign responsibilities to separate classes
and hide implementation details behind interfaces. A class's fan-in (number of incoming calls from
other classes) times its size is what determines maintenance risk — the more a class is called
from elsewhere, the smaller it should be, because more surface area is now hard to change safely.

Fan-in brackets: 1–10, 11–20, 21–50, 51+. Shrinking a high-fan-in class, or splitting it so each
part has a lower fan-in, is progress.

## Root cause: the "large class smell"

Classes rarely start large. They grow one reasonable-looking method at a time (a `UserService`
starts with load/exists/changeInfo, then gains notification methods, then search/block methods)
until every loosely user-related feature defaults into it. At that point even a small internal
change risks breaking distant, unrelated callers.

## How to fix it

- **Split classes by responsibility** — group methods by the concern they serve (notifications,
  blocking, profile management) into separate classes, then rewire callers. Each caller now
  depends on a smaller, more specific surface instead of one large one.
- **Hide specialized implementations behind interfaces** — when a class grows advanced features
  most callers don't need, define a narrow interface exposing only what the common caller uses,
  and have callers depend on that. Only introduce an interface if at least two classes implement
  it, or if the point is limiting what callers of one class can see.
- **Replace custom utility code with a library** — `StringUtils`/`FileUtils`-style classes are
  inherently high fan-in. Keep them small and prefer a well-known library or newer language
  features, so the unavoidable fan-in points at very little of your own code.

Splitting a class changes its callers' imports; that is internal. If the class is itself part of
an external interface, see the invariants in `SKILL.md`.
