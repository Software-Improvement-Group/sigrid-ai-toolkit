# Module Coupling

For each module, count the number of *incoming* dependencies (fan-in):
invocations, imports, or usages from other modules. Aggregate the percentage of
total LOC in modules within each fan-in bracket.

| Risk      | Incoming dependencies (fan-in) |
|-----------|--------------------------------|
| Low       | 0–10                           |
| Moderate  | 11–20                          |
| High      | 21–50                          |
| Very high | 51+                            |

**Why it influences its sub-characteristics:**

- **Modifiability** — modules with high fan-in have many dependents, so changes
  ripple widely and are more likely to introduce defects elsewhere.
- **Modularity** — high coupling between modules reduces the ability to change
  or replace them independently.

**Guidance:** Separate concerns in modules. Modules that are both very large and
have many dependencies tend to have too much responsibility. Reorganizing
functionality generally leads to smaller modules and less coupling.
