# Unit Interfacing

Parameter-object refactors must not change an external interface — see the invariants in
`SKILL.md`.

## Guideline

Limit parameters per unit to **4**. Methods with small interfaces are easier to understand
(callers don't need to track many positional args of the same type — easy to transpose two `int`s
by mistake) and easier to reuse/modify, because they depend on less external input.

Risk brackets: ≤2, 3–4, 5–6, ≥7 parameters. Moving a unit down a bracket is progress even without
reaching ≤2.

## Root cause

A large parameter list is a *symptom*: usually either a poor data model (related values that should
already be one object are passed individually) or a method taking on more than one responsibility
(e.g. building an address string, formatting a message, and sending it, all in one call).

## How to fix it

- **Introduce Parameter Object** — group parameters that are conceptually one thing (an `x,y,w,h`
  rectangle, the parts of an address) into a real domain type. This is the default move, and the
  resulting type is usually reusable elsewhere.
- If the grouped parameters don't naturally cohere and giving them a shared name feels forced,
  consider **Replace Method with Method Object** instead (see [unit-size.md](unit-size.md)): turn
  the method into a small class holding the parameters, with defaults where sensible. This also
  avoids combinatorial overloads for "give me defaults for most params."
- If the parameter object's own constructor now has too many parameters, a finer split exists
  inside it (e.g. `x,y` belong in a nested `Point`, not flat in `Rectangle`).
- If the next method down still receives many parameters, splitting stopped one level too early:
  only the method that actually uses a primitive should receive it unpacked.
- A third-party interface with a long parameter list you must implement is outside your control —
  isolate it behind an adapter so the long list doesn't spread into your own code.
