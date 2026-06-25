# Fix OSH Risk

> **Experimental** — this skill is under active development and will change. Use it directly from the plugin, copy and adapt it to your own workflow, or treat it as a reference for building your own skills. See SKILL.md for the full procedure.
>
> Adaptation ideas: swap GitLab for GitHub, restrict to ticket-only mode, add ecosystems, or adjust the autonomy thresholds.

Remediates Open Source Health findings from Sigrid. Given a set of dependency risks from OSH, this skill researches
fixes, applies version bumps where safe, and creates merge requests. When confidence is low or changes are too large,
it creates a researched GitLab issue instead.

## Setup

### Required integrations

- **Sigrid MCP plugin** — for querying OSH findings (`list_open_source_risks`)
- **GitLab MCP** — for creating merge requests and issues
- **sigrid-ci-feedback skill** — for verifying fixes against Sigrid CI

### Recommended network allowlist

The research agent queries package registries and advisory databases. You can pre-allow these hosts in your
`.claude/settings.json` to streamline the workflow. Scope the allowlist to what makes sense for your environment:

```
pypi.org, npmjs.com, mvnrepository.com, central.sonatype.com,
crates.io, nuget.org, github.com, rustsec.org
```

### Context requirements

The Sigrid customer name and system name must be available in your session context (typically via CLAUDE.md or
AGENTS.md). If your Sigrid baseline branch is not `main` or `master`, specify the branch name in context as well so
the skill targets the correct branch for MRs and Sigrid CI verification.

## Usage

Invoke with `/sigrid-experimental:fix-osh-risk` or let it trigger automatically when you ask Claude to fix
dependency risks.

**Interactive mode** (default) — asks you to confirm scope and whether to create an MR or issue at each step. When
multiple upgrade paths exist, presents them in terms of code impact rather than version numbers.

**Autonomous mode** — processes findings without blocking. Uses the smallest safe version bump and degrades to a GitLab
issue whenever uncertainty is high.

## Example

```
/fix-osh-risk Fix the critical vulnerability in pkg:pypi/requests@2.28.0.
Sigrid customer: acme-corp, system: backend-api. Target branch: develop. Run in autonomous mode.
```

This prompt provides all metadata inline. The full set of parameters:

| Parameter | Required | Default |
|-----------|----------|---------|
| Sigrid customer | Yes | — |
| Sigrid system | Yes | — |
| Target branch | No | `main` |
| Mode | No | Interactive |
| Findings to fix | No | Query all via MCP |

If customer and system are already configured in your session context (via CLAUDE.md or AGENTS.md), you can skip them in the prompt:

```
/fix-osh-risk Fix my critical OSH vulnerabilities.
```

You can also identify findings first using the Sigrid MCP tool (`list_open_source_risks`) and then pass specific results to the skill.

## What it produces

| Situation                                      | Output                                 |
|------------------------------------------------|----------------------------------------|
| Safe version bump available, tests pass        | Merge request                          |
| Risky upgrade, no fix available, or tests fail | GitLab issue with research and options |
| Too many unrelated dependencies at once        | Single consolidated issue              |
