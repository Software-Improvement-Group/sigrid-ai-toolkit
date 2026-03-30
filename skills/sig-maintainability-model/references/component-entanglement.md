# Component Entanglement

Entanglement combines two aspects: how many communication lines exist between
components (density) and how many of those lines form dependency violations such
as cycles or transitive paths (violation degree). Both are normalized against
benchmark maximums and combined into a single score. Continuous scale — lower is
better.

**Why it influences its sub-characteristics:**

- **Modularity** — cycles and transitive dependencies create implicit coupling
  between components that should be independently changeable.

**Guidance:** Clearly define and limit communication lines between components.
Each dependency between components adds complexity to the architecture and makes
it harder to change either component. Some communication patterns, such as
cyclic dependencies, are especially undesirable as they lead to interwoven
components.
