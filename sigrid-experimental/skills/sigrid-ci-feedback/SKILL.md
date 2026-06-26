---
name: sigrid-ci-feedback
user-invocable: true
disable-model-invocation: false
description: >
  Run Sigrid CI locally on the current working tree and return structured quality feedback.
  Use when the user or agent wants maintainability, security, or open source health feedback
  on local code without pushing to a remote or triggering a CI pipeline.
---

# Sigrid CI Feedback

## Preflight checks

Verify these in order before running. If any check fails, stop and ask the user.

1. **Token** — Run `bash ${CLAUDE_SKILL_DIR}/scripts/check_token.sh`. Verifies that `SIGRID_CI_TOKEN` or `SIGRID_TOKEN` is set without reading the value.
2. **Python** — Run `bash ${CLAUDE_SKILL_DIR}/scripts/check_python.sh`. Verifies Python 3 is available. The script prints the Python command to use (`python3` or `python`); capture it for later.
3. **Sigrid CI scripts** — Run `bash ${CLAUDE_SKILL_DIR}/scripts/ensure_sigridci.sh`. Clones the sigridci repository to a temporary directory. The script prints the path to the cloned directory; capture it as `SIGRIDCI_DIR`.
4. **Source root** — If not explicitly provided, run `bash ${CLAUDE_SKILL_DIR}/scripts/find_source_root.sh <project-directory>` to locate the directory containing `sigrid.yaml`/`sigrid.yml` by searching upward. If the script finds nothing, ask the user.
5. **Customer and system** — Must be provided exactly as registered in Sigrid. Only proceed if the user stated them explicitly (e.g. "customer is acme, system is backend"). If the values are implied — e.g. inferred from a company name, repo name, or directory — confirm them before running.
6. **Capabilities** — The Sigrid analyses to run (also known as "models" or "licenses"). Must be provided as a comma-separated string. Valid values: `maintainability`, `osh`, `security`. Example: `maintainability,osh`. No default. When unclear, ask the user which capabilities are needed.

## Running the analysis

```bash
<PYTHON> "$SIGRIDCI_DIR/sigridci/sigridci.py" \
  --customer <CUSTOMER> \
  --system <SYSTEM> \
  --source <SOURCE_ROOT> \
  --out <OUTPUT_DIR> \
  --capability <CAPABILITIES> \
  > /dev/null
```

Where:
- `<PYTHON>` is the command returned by `check_python.sh`
- `<SIGRIDCI_DIR>` is the path returned by `ensure_sigridci.sh`
- `<OUTPUT_DIR>` — a fresh temporary directory (e.g., `mktemp -d`). Do not reuse a previous output directory.

Redirect stdout to `/dev/null`. Stderr is kept for progress and error messages.

The command blocks until analysis completes (up to ~30 minutes).

## Output

Read **only** the markdown file(s) corresponding to the requested capabilities:

| Capability        | File to read           |
|-------------------|------------------------|
| `maintainability` | `feedback.md`          |
| `osh`             | `osh-feedback.md`      |
| `security`        | `security-feedback.md` |

Do **not** read any other files in the output directory. They may contain legacy or misleadingly-named fields not intended for interpretation.

## Publishing

Two flags upload results to Sigrid, making them visible in the dashboard as a permanent snapshot:

- `--publish` — runs the full analysis (returns feedback) **and** publishes the results.
- `--publishonly` — publishes without running analysis (fast, no feedback returned). Typically used in CI when code is merged to main.

The normal workflow is feedback-only (no flag). Only add `--publish` or `--publishonly` when the user asks for it:

- **Explicit** ("use --publish", "run --publishonly", "publish the results to Sigrid") → just do it.
- **Implied** ("show it in the dashboard", "make the team see the scores") → confirm first, explaining that publishing creates a permanent snapshot in Sigrid.

## Avoid

- **NEVER** print, echo, or log the `SIGRID_CI_TOKEN` or `SIGRID_TOKEN` value.
- **NEVER** guess customer or system names — always ask the user when unclear.
