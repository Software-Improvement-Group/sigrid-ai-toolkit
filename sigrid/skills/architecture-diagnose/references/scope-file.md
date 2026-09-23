# Sigrid scope file (`sigrid.yaml`)

Only read this file when you need to propose a scope file change.

## Location

`sigrid.yaml` lives at the repository root. If one doesn't exist yet, create it there. If one
already exists, add to it — never overwrite existing entries.

## Marking a component as utility

```yaml
architecture:
  component_roles:
    - role: utility
      include:
        - "<regex matching component path>"
```

- `include` patterns are regexes matched against Sigrid component paths.
- The role is inherited by all child components.
- Utility components skip Component Coupling and Component Adjacency scoring, and edges to them
  don't count toward other components' coupling.
