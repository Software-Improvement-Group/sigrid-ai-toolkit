---
name: sig-maintainability
description: Get details on SIG maintainability model sub-characteristics (analyzability, modifiability, testability, modularity, reusability), or any of its metrics (volume, duplication, unit size, unit complexity, unit interfacing, module coupling, component independence, component entanglement).
user-invocable: false
---

# SIG Maintainability Model

The SIG maintainability model is the evaluation framework behind Sigrid. It
defines how source code quality is measured and aggregated into ratings.

Ratings predict real-world productivity. Issue resolution and feature delivery
are roughly twice as fast in 4-star systems compared to 2-star systems.

The model evaluates **internal technical quality** of production source code
only — not functional correctness, third-party libraries, generated code, or
build/deployment scripts.

### Star Ratings

SIG uses a 0.5-to-5.5 star rating calibrated against a benchmark of 30,000+
systems. 3 stars is market average; 4 stars is the target for new development.
The benchmark recalibrates annually; a system that stays unchanged will
gradually drift downward.

### Measurement Levels

- **System** — all source code forming the product.
- **Component** — top-level subdivision (typically a directory).
- **Module** — typically a class or file.
- **Unit** — smallest named piece of executable code (method/function).

## Sub-characteristics and Metrics

Evaluated on five ISO 25010 maintainability sub-characteristics: analyzability,
modifiability, testability, modularity, and reusability.

These sub-characteristics are measured using eight metrics. All risk-profile
metrics are weighted by lines of code, not by count — a large complex unit
influences the rating more than a small one.

- **Volume** — Total system size in person-years, normalized across languages.
  Influences analyzability, testability.
- **Duplication** — Percentage of redundant code (clones of ≥6 lines).
  Influences analyzability, modifiability.
- **Unit Size** — Distribution of unit lengths; what % of code lives in large
  units. Influences analyzability, reusability.
- **Unit Complexity** — Distribution of McCabe cyclomatic complexity across
  units. Influences modifiability, testability.
- **Unit Interfacing** — Distribution of parameter counts across unit
  signatures. Influences reusability.
- **Module Coupling** — Distribution of incoming dependencies (fan-in) across
  modules. Influences modifiability, modularity.
- **Component Independence** — Percentage of code hidden from other top-level
  components. Influences testability, modularity.
- **Component Entanglement** — Degree of cyclic/transitive dependency
  anti-patterns between components. Influences modularity.

**Interpreting findings:** Star rating targets depend on context. Risk
categories indicate where to look, not what to fix — medium risk is not
inherently problematic. Judge findings by the principles in each metric's
guidance (e.g., does this unit have a single clear responsibility?).

When asked about a specific metric, read `references/<metric-name>.md` before
answering. Use the guidance section to frame recommendations — not the risk
category a finding falls in.