# Sigrid CI Feedback

> **Experimental** — this skill is under active development and will change. Use it directly from the plugin, copy and adapt it to your own workflow, or treat it as a reference for building your own skills. See SKILL.md for the full procedure.

Runs Sigrid CI locally on the current working tree and returns structured quality feedback. Results are never published to Sigrid unless explicitly requested.

## What it does

1. Verifies prerequisites (token, Python, sigridci scripts, source root)
2. Runs the Sigrid CI analysis locally
3. Returns maintainability, security, or OSH feedback as markdown

## Prerequisites

- `SIGRID_CI_TOKEN` or `SIGRID_TOKEN` environment variable set
- Python 3.7+
- Network access to `github.com` (to clone sigridci scripts), alternatively point to a local clone in your prompt
- Network access to `sigrid-says.com`
- A `sigrid.yaml` / `sigrid.yml` in the project tree, alternatively state the Sigrid system root in your prompt

## Usage

```
/sigrid-experimental:sigrid-ci-feedback for maintainability on customer "corp" and system "backend"
```
