# Change Feedback

> **Adapting this skill.** Configure it by running `/sigrid:setup` to set your customer, system, and conventions in the profile — these survive plugin updates. See SKILL.md for the full procedure.

Runs Sigrid CI locally on the current working tree and returns structured quality feedback. This is strictly feedback-only — nothing is ever published to Sigrid or visible on the dashboard.

## What it does

1. Verifies prerequisites (token, Python, sigridci scripts, source root)
2. Runs the Sigrid CI analysis locally via `agents.py`
3. Returns maintainability, security, or OSH feedback as structured JSON

## Prerequisites

- `SIGRID_CI_TOKEN` or `SIGRID_TOKEN` environment variable set
- Python 3.7+
- Network access to `github.com` (to clone sigridci scripts), alternatively point to a local clone in your prompt
- Network access to `sigrid-says.com`
- A `sigrid.yaml` / `sigrid.yml` in the project tree, alternatively state the Sigrid system root in your prompt

## Usage

```
/sigrid:change-feedback for maintainability on customer "corp" and system "backend"
```
