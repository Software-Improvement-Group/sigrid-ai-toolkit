---
name: sigrid-ci-feedback
user-invocable: true
description: >
  Run Sigrid analysis locally on the current working tree and return structured
  maintainability, security, and open-source-health feedback — before committing or pushing, without
  triggering a remote CI pipeline. Use when the user wants Sigrid's verdict on
  local changes Sigrid has not analysed yet. Trigger on "run Sigrid on my changes", "check this before
  I push", "sigrid ci", or "what would Sigrid say about my current code".
---

# Sigrid CI Feedback

## Preflight checks

Verify these in order before running. If any check fails, stop and ask the user.

1. **Token** — Run `bash ${CLAUDE_SKILL_DIR}/scripts/check_token.sh`. Verifies that `SIGRID_CI_TOKEN` or `SIGRID_TOKEN` is set without reading the value. Note: this is a shell environment variable the user exports themselves — it is **separate** from the MCP `sigrid_token` set via `/plugin` config (that one lives in the OS keychain and is not accessible to this local script). If the check fails, ask the user to `export SIGRID_CI_TOKEN=<their Sigrid token>`; do not point them at the keychain token.
2. **Python** — Run `bash ${CLAUDE_SKILL_DIR}/scripts/check_python.sh`. Verifies Python 3 is available. The script prints the Python command to use (`python3` or `python`); capture it for later.
3. **Sigrid CI scripts** — Run `bash ${CLAUDE_SKILL_DIR}/scripts/ensure_sigridci.sh`. Clones the sigridci repository to a temporary directory. The script prints the path to the cloned directory; capture it as `SIGRIDCI_DIR`.
4. **Source root** — If not explicitly provided, run `bash ${CLAUDE_SKILL_DIR}/scripts/find_source_root.sh <project-directory>` to locate the directory containing `sigrid.yaml`/`sigrid.yml` by searching upward. If the script finds nothing, ask the user.
5. **Customer and system** — Must match what is registered in Sigrid. Read them from the Sigrid profile (`${CLAUDE_PLUGIN_DATA}/CLAUDE.md`, written by `/sigrid:setup`), or use values the user stated explicitly (e.g. "customer is acme, system is backend"). The profile may list several systems; select the one whose `Repo` key matches the current repository, per the profile's resolution rule. If the values are only implied — inferred from a company name, repo name, or directory — or the match is ambiguous, confirm them before running. Whenever any profile-covered setting is established during the run by asking or stated inline (customer/system, capabilities preferences, or any other), write it back into the profile additively (keyed by the current repo's remote where system-specific) so future runs resolve without asking. Never write the token to the profile.
6. **Capabilities** — The Sigrid analyses to run (also known as "models" or "licenses"). Must be provided as a comma-separated string. Valid values: `maintainability`, `osh`, `security`. Example: `maintainability,osh`. No default. When unclear, ask the user which capabilities are needed.

## Running the analysis

```bash
<PYTHON> "$SIGRIDCI_DIR/sigridci/sigridci.py" \
  --customer <CUSTOMER> \
  --system <SYSTEM> \
  --source <SOURCE_ROOT> \
  --out <OUTPUT_DIR> \
  --capability <CAPABILITIES> \
  --disable-onboarding \
  > /dev/null
```

Where:
- `<PYTHON>` is the command returned by `check_python.sh`
- `<SIGRIDCI_DIR>` is the path returned by `ensure_sigridci.sh`
- `<OUTPUT_DIR>` — a fresh temporary directory (e.g., `mktemp -d`). Do not reuse a previous output directory.

Include `--disable-onboarding` **only for feedback-only runs** (no publish flag). Without it, sigridci on-boards — i.e. publishes — a not-yet-existing system even in feedback mode, which a local check must never do. Omit the flag when publishing (`--publish`/`--publishonly`), since publishing is the intended way to on-board. When the system does not exist, this run exits non-zero and writes no feedback file (the `System is not yet on-boarded to Sigrid` message goes to stdout, which this command discards) — so treat *non-zero exit with no feedback file* as "system not on-boarded", report it to the user (it is not a crash), and do not retry.

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
