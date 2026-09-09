# Resolve Security Findings

> **Adapting this skill.** Configure it by running `/sigrid:setup` to set your customer, system, and the "Security findings triage" settings (security model) in the profile. These survive plugin updates.

Triages Sigrid security findings one by one: classifies each as false positive, accepted risk, or will-fix, writes the decision back to Sigrid, and fixes the code when warranted.

## What it does

1. Resolves a finding ID, a pasted finding, or a bulk backlog to work through
2. Reads the flagged code and its context, then classifies it against an evidence gate — false
   positive or accepted risk require a named file:line and reason, otherwise it defaults to will-fix
3. Fixes will-fix findings in the working tree and checks the change with `guardrails_quality_check`
4. Writes the classification and remark back to Sigrid via `update_finding_status`

## Prerequisites

- Sigrid MCP: `get_finding`, `security_get_findings`, `update_finding_status`, `guardrails_quality_check`
- Sigrid customer and system in the profile (`/sigrid:setup`), plus its "Security findings triage"
  section

## Usage

```
/sigrid:resolve-security-findings Triage finding 3f9a1c2e-7b4d-4a10-9e2f-1a2b3c4d5e6f
```

```
/sigrid:resolve-security-findings Work through the security backlog under src/payments/ in autonomous mode
```

Default is **interactive** — it proposes classifications and asks before writing or committing.
**Autonomous** mode only runs when explicitly requested — it writes and commits without blocking.
