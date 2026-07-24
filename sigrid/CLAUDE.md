# Sigrid profile

This file is the **customization surface** for the Sigrid plugin. It captures your team's
conventions so the skills (`sigrid-diagnose`, `sigrid-improve`, `fix-osh-risk`,
`sigrid-ci-feedback`) produce guidance specific to you instead of generic output.

**This is a template.** The live copy that the skills read lives outside the plugin, at a fixed,
version-independent path:

```
~/.claude/plugins/config/sigrid-ai-toolkit/sigrid/CLAUDE.md
```

This is deliberately **not** under `~/.claude/plugins/cache/` — the cache is version-scoped and
replaced on every update, whereas the `config/` path is stable. So your customization
**survives `/plugin update`** and is never clobbered when the plugin auto-updates on newer commits.

Populate it by running `/sigrid:setup`, which interviews you and writes the file. You can also
edit it by hand at any time. Skills fall back to asking (interactive) or aborting (autonomous) for
anything that is missing here.

---

## Sigrid system

Both appear in your Sigrid URL: `sigrid-says.com/<customer>/<system>`.

- **Customer**: <your Sigrid customer/account name, exactly as registered — lowercase alphanumeric, min 2 chars>
- **System**: <your Sigrid system name, exactly as registered — lowercase alphanumeric segments separated by hyphens>
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
