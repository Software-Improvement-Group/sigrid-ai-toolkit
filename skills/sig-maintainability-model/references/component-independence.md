# Component Independence

Each module is classified as:

- **Hidden**: no incoming dependencies from modules in *other* components
- **Exposed**: has ≥1 incoming dependency from another component

Component independence = percentage of total LOC in hidden modules. Only
incoming cross-component dependencies matter; outgoing dependencies do not
affect this metric. Continuous scale — higher hidden % is better.

**Why it influences its sub-characteristics:**

- **Testability** — hidden modules can be tested in isolation without needing to
  account for external consumers.
- **Modularity** — components with a high percentage of hidden code can evolve
  independently without cross-component impact.

**Guidance:** Design architecture components to be loosely coupled. Separate each
component into an interface that receives incoming communication from other
components and an internal part. Changes to the interface may affect dependent
components, so keep the interface as small as possible.
