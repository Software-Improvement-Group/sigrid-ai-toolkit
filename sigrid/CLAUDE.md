# Sigrid profile

This file is the **customization surface** for the Sigrid plugin. It captures your team's
conventions so the skills (`sigrid-diagnose`, `sigrid-improve`, `fix-osh-risk`,
`change-feedback`) produce guidance specific to you instead of generic output.

**This is a template.** The live copy that the skills read lives in the plugin's persistent data
directory, exposed by Claude Code as `${CLAUDE_PLUGIN_DATA}`:

```
${CLAUDE_PLUGIN_DATA}/CLAUDE.md
```

For this plugin that resolves to `~/.claude/plugins/data/sigrid-sigrid-ai-toolkit/CLAUDE.md`. This is
the officially supported per-plugin data location: it lives **outside** the version-scoped
`~/.claude/plugins/cache/` (which is replaced on every update), so your customization
**survives `/plugin update`** and is never clobbered when the plugin auto-updates on newer commits.

Populate it by running `/sigrid:setup`, which interviews you and writes the file. You can also
edit it by hand at any time. Skills fall back to asking (interactive) or aborting (autonomous) for
anything that is missing here.

---

## Sigrid systems

Each Sigrid *system* corresponds to one codebase, so you may work across several. List every system
here — one block per system. Both values appear in your Sigrid URL: `sigrid-says.com/<customer>/<system>`.

**How skills pick the active system:** they match the current repository's git remote
(`git remote get-url origin`) against each block's `Repo` key. Match on the meaningful identity —
`host/owner/repo` — not on an exact string: treat SSH and HTTPS forms as equal, and ignore a trailing
`.git`, a trailing slash, and case (e.g. `git@github.com:acme/payments-api.git`,
`https://github.com/acme/payments-api`, and `github.com/acme/payments-api` all denote the same repo).
On exactly one match, that system is used. If nothing matches, more than one matches, or several
blocks have no `Repo` key, the skill asks (interactive) or aborts (autonomous) rather than guessing. A
profile with a single block and no `Repo` key is always used unconditionally — the simple
single-system case needs no key.

**Persist what gets resolved.** This profile is the single source of truth for every setting it
covers — not just customer/system, but baseline branch, git-host conventions, behavior preferences,
and anything else recorded here. Whenever a skill establishes such a setting during a run — by asking,
or from a value the user states inline — rather than reading it from this profile, it writes that
value back before continuing (filling in an existing block/field or adding a new one, keyed by the
current repo's remote where it is system-specific). The next run then resolves silently. This write is
additive: never overwrite a populated field with a different value without confirming, and never write
the Sigrid token here.

Copy the block below once per system:

### <label, e.g. payments-api>
- **Repo**: <git remote used to match the working dir, e.g. `github.com/acme/payments-api` — omit only if this is your single system>
- **Customer**: <lowercase alphanumeric, min 2 chars>
- **System**: <lowercase alphanumeric segments separated by hyphens>
- **Baseline branch**: <the branch Sigrid analyses, e.g. `main` — used for change-request targets and CI verification>

## Git host conventions

The skills express forge actions in terms of a `~~git host` capability and dispatch to whichever
git-host MCP you have connected (GitLab, GitHub, …). This section records the asymmetries that
abstraction cannot cover.

- **Forge**: <GitLab | GitHub | other>
- **Change request term**: <Merge Request (GitLab) | Pull Request (GitHub)>
- **Branch naming**: <e.g. `fix/osh-<dependency>`, `refactor/<area>`>
- **Required approvals / reviewers**: <e.g. 1 approval, CODEOWNERS, none>
- **Open as draft?**: <yes | no>
- **Labels / milestones that actually exist**: <list, or "none — do not set any">

## Customizing behavior

Beyond the settings above, describe in plain language how you want the skills to behave — there is no
fixed schema, so write whatever matters to your team. The skills read this and take it into account.

For example, if you want to change the default behavior, you might note things like when to open a change
request versus an issue; and who to notify.
