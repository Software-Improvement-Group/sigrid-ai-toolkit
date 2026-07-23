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

The profile is written outside the plugin, at a fixed, version-independent path so it survives
`/plugin update`:

```
~/.claude/plugins/config/sigrid-ai-toolkit/sigrid/CLAUDE.md
```

This is deliberately **not** under `~/.claude/plugins/cache/` — the cache is version-scoped and
replaced on every update. The `CLAUDE.md` shipped with the plugin is only a template (it
too is replaced on update); never write user data there.

## Procedure

1. **Read the template.** Open `CLAUDE.md` at the plugin root to get the current field
   list and inline guidance. Use it as the structure for both the interview and the file you write.

2. **Check for an existing profile.** Check the path above. If it exists, read it and treat this as
   an **update** — show the current values and only ask about fields the user wants to change or that
   are still placeholders. Never silently overwrite populated fields.

3. **Interview.** Ask in small batches, not one giant form. Cover the concrete settings first:
   - **Sigrid system** — customer name and system name, exactly as registered in Sigrid (do not
     infer from company or repo name — confirm). Baseline branch Sigrid analyses.
   - **Git host conventions** — forge (GitLab/GitHub/other); MR-vs-PR wording; branch naming;
     required approvals; draft behaviour; which labels/milestones actually exist.

   Then, lightly, ask whether they want to customize any skill behavior — in plain language, not a
   fixed form. Only capture what they volunteer (e.g. off-limits code, when to
   open a change request vs. an issue, who to notify). Do not push for answers to every possible
   behavior; the defaults are fine when they have no preference.

4. **Write the profile.** Create the parent directories if needed and write the filled-in file to
   the path above. Preserve the template's section structure so skills can find fields reliably.

5. **Confirm.** Show the user a short summary of what was written and the path, and remind them they
   can re-run `/sigrid:setup` or edit the file directly to change conventions later.

## Notes

- This skill only writes the profile. It never touches project code or calls the Sigrid MCP.
- Never store the Sigrid API token here — the token is handled by plugin `userConfig` and lives in
  the OS keychain.
