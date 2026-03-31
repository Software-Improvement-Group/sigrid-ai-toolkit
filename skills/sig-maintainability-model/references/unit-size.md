# Unit Size

Count the lines of code within each unit (method/function body). Aggregate the
percentage of total LOC that falls in each size bracket. The rating is based on
the distribution across these buckets — not the count of units.

| Risk      | Unit size |
|-----------|-----------|
| Low       | 1–15 LOC  |
| Moderate  | 16–30 LOC |
| High      | 31–60 LOC |
| Very high | 61+ LOC   |

**Why it influences its sub-characteristics:**

- **Analyzability** — long units are harder to read and understand, making it
  more difficult to assess the impact of a change.
- **Reusability** — long units tend to combine multiple responsibilities, making
  them harder to extract and reuse in other contexts.

**Guidance:** Write short units of code. A unit should do only one thing, which
typically leads to a shorter unit. A larger unit typically has multiple
responsibilities. Splitting such a unit into one unit per responsibility makes
it easier to maintain, as each unit will have only one reason to change.
