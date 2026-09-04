# Fix OSH Risk

Remediates Open Source Health findings from Sigrid. Given a set of dependency risks from OSH, this skill researches
fixes, applies version bumps where safe, and creates change requests (merge/pull requests). When confidence is low or
changes are too large, it creates a researched issue instead.

> **Adapting this skill.** Configure it by running `/sigrid:setup` to set your git-host conventions and any
> behavior preferences in the profile — these survive plugin updates.

## Setup

### Required integrations

- **Sigrid MCP** — for querying OSH findings (`list_open_source_risks`)
- **A `~~git host` MCP** — any git-host MCP (GitLab, GitHub, …) for creating change requests and issues. The skill is
  forge-agnostic and does not ship a git-host server; connect the one your team uses. If none is connected, the skill
  stops rather than producing a local-only change.
- **change-feedback skill** — for verifying fixes against Sigrid CI

### Recommended network allowlist

The research agent queries package registries and advisory databases. You can pre-allow these hosts in your
`.claude/settings.json` to streamline the workflow. Scope the allowlist to what makes sense for your environment:

```
pypi.org, npmjs.com, mvnrepository.com, central.sonatype.com,
crates.io, nuget.org, github.com, rustsec.org
```

### Context requirements

The Sigrid customer name, system name, baseline branch, and git-host conventions come from the **Sigrid profile**
(`${CLAUDE_PLUGIN_DATA}/CLAUDE.md`, i.e. `~/.claude/plugins/data/sigrid-sigrid-ai-toolkit/CLAUDE.md`). Run `/sigrid:setup` to populate it. If the
baseline branch is not `main`, set it there so the skill targets the correct branch for change requests and Sigrid CI
verification.

## Usage

Invoke with `/sigrid:fix-osh-risk` or let it trigger automatically when you ask Claude to fix dependency risks.

**Interactive mode** (default) — asks you to confirm scope and whether to create a change request or issue at each
step. When multiple upgrade paths exist, presents them in terms of code impact rather than version numbers.

**Autonomous mode** — processes findings without blocking. Uses the smallest safe version bump and degrades to an
issue whenever uncertainty is high.

## Example

```
/sigrid:fix-osh-risk Fix the critical vulnerability in pkg:pypi/requests@2.28.0. Run in autonomous mode.
```

The Sigrid customer, system, and target branch come from your profile. You can still override them inline:

| Parameter | Required | Default |
|-----------|----------|---------|
| Sigrid customer | Yes | from profile |
| Sigrid system | Yes | from profile |
| Target branch | No | profile baseline branch, else `main` |
| Mode | No | Interactive |
| Findings to fix | No | Query all via MCP |

If customer and system are already in your profile, you can skip them in the prompt:

```
/sigrid:fix-osh-risk Fix my critical OSH vulnerabilities.
```

You can also identify findings first using the Sigrid MCP tool (`list_open_source_risks`) and then pass specific results to the skill.

## What it produces

| Situation                                      | Output                                    |
|------------------------------------------------|-------------------------------------------|
| Safe version bump available, tests pass        | Change request (merge/pull request)       |
| Risky upgrade, no fix available, or tests fail | Issue with research and options           |
| Too many unrelated dependencies at once        | Single consolidated issue                 |
