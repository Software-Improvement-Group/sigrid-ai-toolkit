---
name: setup
user-invocable: true
description: >
  Set up (or update) the Sigrid profile for this environment. Interviews the user for their
  Sigrid customer/system, git host conventions, and any behavior preferences, then writes them to
  the plugin profile that the Sigrid skills read. Use when first installing the Sigrid plugin, when a skill reports the profile is
  missing, or when conventions change. Trigger on "set up Sigrid", "configure Sigrid",
  "Sigrid onboarding", or "my Sigrid customer/system is ...".
---

# Sigrid setup

Populates the **Sigrid profile** — the customization surface every Sigrid skill reads.

## Where the profile lives

The profile is written to the plugin's persistent data directory, exposed as `${CLAUDE_PLUGIN_DATA}`,
so it survives `/plugin update`:

```
${CLAUDE_PLUGIN_DATA}/CLAUDE.md
```

This is the officially supported per-plugin data location — it lives **outside** the version-scoped
`~/.claude/plugins/cache/`, which is replaced on every update. The `CLAUDE.md` shipped with the plugin
is only a template (it too is replaced on update); never write user data there.

## Procedure

1. **Read the template.** Open `CLAUDE.md` at the plugin root to get the current field
   list and inline guidance. Use it as the structure for both the interview and the file you write.

2. **Check for an existing profile.** Read `${CLAUDE_PLUGIN_DATA}/CLAUDE.md`. If it exists, treat this as
   an **update** — list the systems already recorded and ask whether the user wants to add a new
   system, edit an existing one, or change the shared conventions. Never silently overwrite populated
   fields.

3. **Interview.** Ask in small batches, not one giant form. Cover the concrete settings first:
   - **Sigrid system(s)** — a profile can hold several systems (one per codebase), so ask whether the
     user works across more than one and capture each. For every system collect customer name and
     system name, exactly as registered in Sigrid (do not infer from company or repo name — confirm),
     plus the baseline branch Sigrid analyses.
     - Hint the user: both can be read straight off their Sigrid URL, which has the shape
       `sigrid-says.com/<customer>/<system>`.
     - Validate against Sigrid's naming rules before writing, and ask again if a value doesn't fit:
       - **customer**: lowercase alphanumeric, minimum 2 characters.
       - **system**: lowercase alphanumeric segments separated by hyphens.
     - **Repo match key** — so skills can auto-select the right system, record how each maps to a
       repository. Run `git remote get-url origin` in the relevant checkout to prefill it. Store it in
       the canonical `host/owner/repo` form (strip any `git@`/`https://` prefix, the `.git` suffix, and
       trailing slash — e.g. `github.com/acme/payments-api`) so matching is form-independent. Only a
       single-system profile may omit the key.
   - **Git host conventions** — forge (GitLab/GitHub/other); MR-vs-PR wording; branch naming;
     required approvals; draft behaviour; which labels/milestones actually exist.

   Then, lightly, ask whether they want to customize any skill behavior — in plain language, not a
   fixed form. Only capture what they volunteer (e.g. off-limits code, when to
   open a change request vs. an issue, who to notify). Do not push for answers to every possible
   behavior; the defaults are fine when they have no preference.

4. **Write the profile.** Ensure the data directory exists first (`mkdir -p "${CLAUDE_PLUGIN_DATA}"`),
   then write the filled-in file to `${CLAUDE_PLUGIN_DATA}/CLAUDE.md`. Preserve the template's section
   structure so skills can find fields reliably.

5. **Confirm.** Show the user a short summary of what was written and the path, and remind them they
   can re-run `/sigrid:setup` or edit the file directly to change conventions later.

## Notes

- This skill only writes the profile. It never touches project code or calls the Sigrid MCP.
- Never store the Sigrid API token in the profile. The MCP token is handled by plugin `userConfig`
  and lives in the OS keychain. Note this keychain token is **not** visible to the `sigrid-ci-feedback`
  skill, which runs Sigrid CI as a local subprocess and reads a separate `SIGRID_CI_TOKEN` (or
  `SIGRID_TOKEN`) shell environment variable the user exports themselves.
