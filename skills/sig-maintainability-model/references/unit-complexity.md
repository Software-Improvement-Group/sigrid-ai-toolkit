# Unit Complexity

McCabe cyclomatic complexity is calculated per unit by counting the number of
decision points (`if`, `for`, `while`, `case`, `&&`, `||`, etc.) plus 1. This
represents the number of independent execution paths through the unit. The
metric aggregates the percentage of total LOC in each complexity bracket.

| Risk      | McCabe complexity |
|-----------|-------------------|
| Low       | 1–5               |
| Moderate  | 6–10              |
| High      | 11–25             |
| Very high | 26+               |

**Why it influences its sub-characteristics:**

- **Modifiability** — complex branching logic is harder to change correctly
  without introducing defects.
- **Testability** — more independent execution paths require more tests to
  achieve adequate coverage.

**Guidance:** Write simple units of code. Each decision point adds complexity to
a unit. Limiting the number of decision points makes it easier to reason about
the decision tree and create appropriate test cases.
