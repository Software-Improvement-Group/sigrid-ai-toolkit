# Unit Complexity

See also [unit-size.md](unit-size.md) — long units and complex units often coincide and share the
Extract Method fix.

## Guideline

Limit branch points per unit to **4** (i.e. cyclomatic/McCabe complexity ≤5). A branch point is
`if`, `case`, `?`, `&&`/`||`, `while`, `for`, `catch` — anywhere execution forks based on a
condition. McCabe complexity = branch points + 1 = the minimum number of test cases needed for
full branch coverage.

Risk brackets: McCabe ≤5, 6–10, 11–25, >25. Moving a unit down a bracket is progress even without
reaching ≤5.

## Root cause patterns

- **Several independent code blocks glued into one unit** — complexity is just the sum of the
  parts. Fix: Extract Method per block (see [unit-size.md](unit-size.md)).
- **Long chain of mutually-exclusive conditionals / long `switch`** — one branch per case, each
  adding to McCabe. Fix: replace the chain with a lookup (a map from condition to value/behavior),
  or go further with **Replace Conditional with Polymorphism** (one type per case implementing a
  shared interface) when the cases are likely to grow or the branches do meaningfully different
  work. The map is quicker; polymorphism is more extensible but spreads code over more classes —
  pick based on how much the case set is expected to change.
- **Deep nesting** (`if` inside `if` inside `if`) — **Replace Nested Conditional with Guard
  Clauses** fixes readability but does *not* reduce McCabe; you still need to extract branches
  into separate methods to lower complexity.

"The domain is inherently complex" doesn't force complex *units*: model a simple default path plus
explicit exceptions instead of spreading it through one method's branches.
