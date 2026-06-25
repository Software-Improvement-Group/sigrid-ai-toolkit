---
name: fix-osh-risk
user-invocable: true
description: >
  Remediate Open Source Health (OSH) findings from Sigrid — vulnerabilities, outdated dependencies,
  license issues, inactive/unstable libraries, and unmanaged dependencies. Produces merge requests
  for confident fixes, or researched GitLab issues when human judgment is needed. Use when the user
  wants to fix OSH findings, resolve dependency vulnerabilities, update outdated libraries, address
  license risks, or act on any Sigrid open source health result. Also trigger when the user mentions
  "fix dependencies", "update vulnerable packages", "OSH remediation", "CVE", "SBOM",
  "dependency risk", or wants to act on open source risks surfaced by Sigrid.
---

# Fix OSH Risk

## Prerequisites

- Sigrid customer and system name must be in context (e.g. AGENTS.md, CLAUDE.md)
- Sigrid MCP plugin available: `list_open_source_risks`
- **GitLab MCP available**: MR and issue creation. This skill targets GitLab exclusively. If the repository remote is not GitLab or cannot be determined: in interactive mode, ask the user to confirm; in autonomous mode, abort immediately with a clear error. Never assume the VCS platform.
- Sigrid CI feedback skill available (for verification)

## Required outcomes

Every invocation of this skill MUST produce exactly one persistent artifact per dependency: either a **GitLab Merge Request** or a **GitLab Issue**. Local-only changes (edits without a branch/MR, text summaries, verbal recommendations) are never acceptable outcomes. If you cannot produce an MR or issue — because of missing permissions, wrong VCS platform, network failures, or any other reason — fail explicitly rather than degrading to informal output.

## Modes

**Interactive** — asks at each decision point. The user confirms scope and artifact type. If a prerequisite is missing, ask the user to resolve it. When multiple upgrade paths exist, present them in terms of what code changes they require (e.g. "patch bump, no code changes needed" vs "minor bump, one deprecated API call to update") rather than asking the user to pick a version number.

**Autonomous** — follows defaults, never blocks. When uncertain, degrades to a GitLab issue rather than asking. If a prerequisite or required input is missing, abort with a clear error.

| Decision point | Interactive | Autonomous |
|----------------|-------------|------------|
| Which findings to act on | User confirms or selects | All provided findings |
| Multiple upgrade paths | Ask user, framed as code impact | Smallest sufficient bump |
| Transitive override risk | Confirm | Apply if clean; ticket if not |
| No patched version exists | Ask: skip or ticket? | Ticket |
| Tests fail after bump | Ask: MR anyway or ticket? | Ticket |
| Final artifact type | Can ask "MR or ticket?" | Follow risk-type routing |

## Procedure

A pipeline with off-ramps. At any stage, the agent can stop and create a GitLab issue instead of continuing — this is the preferred outcome when confidence is low or changes become large.

### Stage 1 — Identify

The input findings must already be in context (provided by the user or a preceding workflow step). If not: in interactive mode, ask whether to query Sigrid MCP and with what scope. In autonomous mode, fail.

Group findings by dependency (purl — Package URL identifier). One dependency may have multiple CVEs/risks — the fix unit is the dependency, not the individual finding. One version bump can clear several findings at once.

If a dependency appears in multiple manifests, keep them in a single fix unit. A version bump may require code changes in every module that uses the library, so these must land together in one MR.

This skill processes dependencies sequentially, one at a time. In interactive mode, if the user provides multiple dependencies, ask which one to start with or whether to process all sequentially. In autonomous mode, process them sequentially — but if the total set is large enough that combining fixes into a single MR would make it unreviewable (rough guide: more than 5 unrelated dependencies), create a single consolidated GitLab issue listing all findings and recommended actions instead.

### Stage 2 — Fast-path bump (vulnerability only)

If ALL of these conditions are met, skip directly to Stage 3 (Implement) without spawning the research agent:

1. The finding's risk type is **vulnerability** (no freshness, license, activity, or stability risks on this dependency)
2. A next version is available in the finding data
3. The bump is a patch or minor version increment

Apply the next version bump and run Sigrid CI. If CI confirms all vulnerabilities on this dependency are resolved → proceed to Stage 4.

If CI still reports risks (e.g. the nextVersion doesn't cover all CVEs, or introduces new findings) → continue to Stage 2b (Research) with the knowledge that `nextVersion` was insufficient.

### Stage 2b — Research

For each dependency, spawn the `osh-researcher` subagent (registered at plugin level in `modernization-experimental/agents/`) with the library name, ecosystem, and clear descriptions of each risk. The researcher only has web access — no project files, no MCP servers, no internal context.

Make risk descriptions actionable for web research: a CVE ID is self-explanatory, but Sigrid-specific risks (freshness, activity, stability, management) need context the researcher can't look up. For example, don't just say "freshness risk" — say "current version is 2.3.1, latest available is 4.0.0, last updated 3 years ago." Give the researcher enough to work with without exposing internal system details.

After research completes, determine the path forward based on risk type:

| Risk type | Typical resolution | Can produce MR? |
|-----------|-------------------|-----------------|
| Vulnerability | Bump to patched version | Yes |
| Freshness | Bump to latest | Yes |
| License | Add missing license declaration, or replace library | Only if declaring a license; replacing → ticket |
| Activity | Replace abandoned library | No — always ticket |
| Stability | Pin stable version or replace | No — always ticket |
| Management | Declare in package manager | Yes, if trivial (e.g. adding to manifest) |

If the research agent finds conflicting fix ranges (multiple CVEs that can't all be satisfied by a single version), off-ramp to a ticket.

### Stage 3 — Implement

Only reached for risk types that can produce MRs (either via the fast-path bump or after research).

1. **Create a branch first** — do not modify any files until you have created a dedicated branch off the main branch. Use a short readable name like `fix/osh-commons-lang3` or `fix/osh-lodash` — don't include the full purl. This is a hard gate: no branch means no changes.
2. Apply the version bump or fix using ecosystem-appropriate mechanics.
3. Run tests if a test command is available.
4. **Run Sigrid CI verification** (mandatory). Invoke the `sigrid-ci-feedback` skill on the working tree to run Sigrid CI in OSH mode. This is the only way to confirm the original finding is actually resolved — without it, the fix is unverified and must not be shipped as an MR. If the finding still appears: try an alternative version from the researcher's suggestions if one exists. If no alternatives remain, off-ramp to a ticket.

**When to off-ramp to a ticket instead:**
- Changes become widespread (touching many files, large diff)
- Tests fail and the fix isn't obvious
- Resolution introduces new dependency conflicts

Reason about risk rather than following a rigid threshold. A patch bump in a well-tested npm package is low risk; a minor bump in a Maven library with no semver guarantees deserves more caution. But remember: MRs get human review anyway, so moderate uncertainty is acceptable.

### Stage 4 — Artifact

Before creating any artifact, check for an existing branch/MR/issue for this dependency. If one exists, comment on it with new insights from your research instead of creating a duplicate.

All MR and issue descriptions start with this banner:

```
🤖 **Generated agentically by Sigrid fix-osh-risk**

---
```

**Merge Request** (confident path):
- Target: main branch (unless specified otherwise)
- Description includes: dependency purl, CVEs/risks cleared, old→new version, direct/transitive/override, advisory refs, residual risk, what was NOT verified

**GitLab Issue** (off-ramp path):
- Research why the dependency was included that way and what concrete options exist
- Include source URLs from the research agent so developers can verify
- Include the attempted diff if one was generated before off-ramping
- Keep it lean — only genuinely useful content, never filler

Never invent metadata that wasn't explicitly provided or discovered during the workflow. Labels, milestones, assignees, and other GitLab fields must only be set if they concretely exist in the project — never guess or hallucinate values. If unsure whether a label exists, omit it.

Note: OSH findings have no status update API — `edit_finding_status` does not exist for OSH. Never attempt to mark findings as resolved via API. The MR or issue is the only persistent outcome.

## Error handling

- Research agent returns no options: off-ramp to ticket with whatever context is available.
- Network unavailable: degrade to ticket-only mode for all findings.
