# Duplication

A code fragment is considered duplicated if it is ≥6 lines long and occurs
(modulo whitespace) in at least one other location. Redundant lines = (number of
occurrences − 1) × fragment length. The metric is the percentage of redundant
lines over all lines. Rated as a single percentage against benchmark
distribution.

**Why it influences its sub-characteristics:**

- **Analyzability** — duplicated code forces developers to locate and understand
  all copies of a fragment to assess the impact of a change or diagnose a
  defect.
- **Modifiability** — changes must be applied consistently to every copy,
  increasing the risk of introducing defects when one copy is missed.

**Guidance:** Write code once. Duplicated code wastes time, as future changes
will need to be applied to all copies. This might also introduce bugs if you
inadvertently forget to update one of the copies.
