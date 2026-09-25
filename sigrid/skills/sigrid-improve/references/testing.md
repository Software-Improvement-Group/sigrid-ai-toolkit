# Tests during a refactor

A refactor must not change behavior; the tests are how you know it didn't.

- **Run the covering tests before and after** the change (see `SKILL.md` Step 3 and Step 4).
- **No coverage for the code you're changing?** Add tests for that code only — normal and edge
  cases (empty, invalid, boundary input), since edge cases are where refactoring bugs hide. Don't
  backfill coverage for code you aren't touching.
- **Keep tests isolated** — one behavior per test, no shared state left by other tests. Stub or
  mock collaborators you don't want live, using the project's existing test tooling.
- **Update tests to the new shape of the code**, not the old one, in the same change.
- **Harder to test after the refactor than before** means the refactor went the wrong way: the new
  unit is still doing too much, or depends on too much.
