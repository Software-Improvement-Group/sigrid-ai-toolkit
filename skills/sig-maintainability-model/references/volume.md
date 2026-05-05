# Volume

Lines of code per file are counted, then normalized using industry-average
productivity factors per programming language (e.g. Python LOC is weighted
differently than Java LOC). This yields a language-independent person-year
estimate.

Volume is benchmarked on an absolute scale relative to the benchmark. Larger
systems indicate higher project risk. As of the 2026 model, volume is reported
for context and does not affect the maintainability rating.

**Why it matters:**

- **Analyzability** — larger systems take more effort to navigate and understand
  when assessing the impact of a change or diagnosing a defect.
- **Testability** — larger systems require more effort to establish test
  criteria and achieve meaningful coverage.

**Guidance:** Keep your codebase small where feasible, but focus improvement
efforts on the maintainability metrics that development teams can directly
influence.
