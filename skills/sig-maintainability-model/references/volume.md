# Volume

Lines of code per file are counted, then normalized using industry-average
productivity factors per programming language (e.g. Python LOC is weighted
differently than Java LOC). This yields a language-independent person-year
estimate.

No standard risk buckets — volume is rated on an absolute scale relative to the
benchmark. Larger systems score lower.

**Why it influences its sub-characteristics:**

- **Analyzability** — larger systems take more effort to navigate and understand
  when assessing the impact of a change or diagnosing a defect.
- **Testability** — larger systems require more effort to establish test
  criteria and achieve meaningful coverage.

**Guidance:** Keep your codebase small. Very large systems need large teams to
maintain them. Splitting a monolith into subsystems is generally more flexible,
as it allows different teams to work independently on their own subsystem.
