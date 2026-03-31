# Unit Interfacing

Count the number of formal parameters (arguments) in the signature/declaration
of each unit. Aggregate the percentage of total LOC in each bracket.

| Risk      | Parameters |
|-----------|------------|
| Low       | 0–2        |
| Moderate  | 3–4        |
| High      | 5–6        |
| Very high | 7+         |

**Why it influences its sub-characteristics:**

- **Reusability** — units with many parameters are tightly coupled to their
  calling context, making them harder to reuse elsewhere.

**Guidance:** Keep unit interfaces small. Avoid creating units that take many
parameters, as it makes them inconvenient to call and generally indicates a lack
of abstraction. Introduce a parameter object if the same parameter list is
passed to several different units.
