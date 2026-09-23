# Sigrid's architecture graph

## How it's built

- Edges = resolved calls, file→file (calls, constructor/static calls, extends/implements).
- Imports without a resolved call create no edge; facades/re-exports are skipped through to the real callee.
- Exactly one candidate definition → edge. Zero or ambiguous candidates → dropped. Dynamic dispatch, DI, reflection,
  and string-based lookups produce no edges.
- **Under-reports, never over-reports.** No edge means "not measured"
- Edge types: `CODE_CALL`, `INTERFACE_CALL` (REST/messaging)
- Test/generated code excluded
- Graph reflects the baseline branch at last analysis, never the working tree.

## Components

- A component = a directory + everything below it
- Loose files in a dir that also has subdirs go into a synthetic `<dir>$Files` child 
- **Utility role**: name (or ancestor's name) matches `common/core/shared/util(s)/lib(s)/helper(s)/framework` → no
  coupling/adjacency rating (`null`), and edges to it don't count toward others' coupling. Directories that serve a
  utility role but don't match the name pattern can be marked explicitly in `sigrid.yaml` — see
  `references/scope-file.md` for the schema.

## The five metrics

External edge = resolved call with exactly one endpoint inside component C.

| Metric                       | Value                                                                        | Changed by                                   |
|------------------------------|------------------------------------------------------------------------------|----------------------------------------------|
| Code breakdown               | files directly in C                                                          | moving loose files into subdirs              |
| Component coupling           | sum of external edge counts (ancestor edges count, utility edges don't)      | fewer calls crossing the boundary            |
| Component adjacency          | # distinct components at far end of external edges (excl. ancestors/utility) | losing the last edge to a component          |
| Component cohesion           | internal / (internal+external) calls, %                                      | edges becoming internal                      |
| Communication centralization | % of LOC in files with no external edge                                      | a file gaining/losing its last external edge |

Structure rating = geometric mean of these five, blended with children's volume-weighted ratings

## Predicting a change

Always get real edge numbers first — a proposal without them is a guess. Edges the graph can't see (dynamic dispatch
etc.) don't move ratings even if real coupling changes.

- **Move F from A to B**: get F's external edges, split by endpoint (B / A's other files / elsewhere). Edges with B
  become internal (B's cohesion↑, coupling↓); edges with A become external for both (both worse); edges elsewhere
  unchanged. Worth it if F's count-with-B clearly beats count-with-A, and neither ends below target.
- **Split a file**: edges follow whichever unit defines the callee — read the source to know which units callers
  actually use.
- **Add a facade**: only counts if it contains code calling the target itself. Coupling/adjacency to the target
  component unchanged (edges still cross), but centralization rises (only the facade now holds them); cohesion shifts
  only if internal calls outweigh collected external ones.
- **Reroute/remove calls**: coupling drops by count removed; adjacency drops only if it was the component's last edge;
  centralization moves only for a file gaining/losing its last external edge.
- **A fix that only makes calls unresolvable is not a fix.** Introducing dynamic dispatch, DI, or string-based lookups
  to replace direct calls removes the edge from Sigrid's graph but doesn't reduce real coupling.
- **Verify without Sigrid**: tools reflect baseline only. Redo the arithmetic by hand from the working tree — count real
  call sites, don't trust imports alone.
