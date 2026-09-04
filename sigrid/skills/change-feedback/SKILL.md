---
name: change-feedback
user-invocable: true
description: >
  Run Sigrid analysis locally on the current working tree and return structured
  maintainability, security, and open-source-health feedback — before committing or pushing, without
  triggering a remote CI pipeline or publishing anything to Sigrid. Use when the user wants Sigrid's
  verdict on local changes Sigrid has not analysed yet. Trigger on "run Sigrid on my changes", "check
  this before I push", "sigrid ci", or "what would Sigrid say about my current code".
---

# Change Feedback

## Preflight checks

Verify these in order before running. If any check fails, stop and ask the user.

1. **Python** — Try `python3 --version`; if that command isn't found, try `python --version` and confirm it reports Python 3.x. Capture whichever command worked as `<PYTHON>` — every step below runs its script via `<PYTHON> <script>.py`. If neither yields Python 3, stop and tell the user to install Python 3.7+.
2. **Token** — Run `<PYTHON> ${CLAUDE_SKILL_DIR}/scripts/check_token.py`. Verifies that `SIGRID_CI_TOKEN` or `SIGRID_TOKEN` is set, and reports its length — nothing else — without reading the value. Note: this is a shell environment variable the user exports themselves — it is **separate** from the MCP `sigrid_token` set via `/plugin` config (that one lives in the OS keychain and is not accessible to this local script). If the check fails, ask the user to `export SIGRID_CI_TOKEN=<their Sigrid token>`; do not point them at the keychain token. This script's output is the complete diagnostic for the token — including later, if `agents.py` itself rejects the token as invalid or too short. There is nothing more to learn by inspecting the environment yourself, and doing so risks leaking the token into the transcript — so don't, even to debug an unexpected error.
3. **Sigrid CI scripts** — Run `<PYTHON> ${CLAUDE_SKILL_DIR}/scripts/ensure_sigridci.py`. Fetches the sigridci repository into a persistent cache (`${CLAUDE_PLUGIN_DATA}/dependency-cache/sigridci`), pulling the latest commit if already cached rather than re-cloning. The script prints the path to the cached directory; capture it as `SIGRIDCI_DIR`.
4. **Source root** — If not explicitly provided, run `<PYTHON> ${CLAUDE_SKILL_DIR}/scripts/find_source_root.py <project-directory>` to locate the directory containing `sigrid.yaml`/`sigrid.yml` by searching upward. If the script finds nothing, ask the user.
5. **Customer and system** — Must match what is registered in Sigrid. Read them from the Sigrid profile (`${CLAUDE_PLUGIN_DATA}/CLAUDE.md`, written by `/sigrid:setup`), or use values the user stated explicitly (e.g. "customer is acme, system is backend"). The profile may list several systems; select the one whose `Repo` key matches the current repository, per the profile's resolution rule. If the values are only implied — inferred from a company name, repo name, or directory — or the match is ambiguous, confirm them before running. Whenever any profile-covered setting is established during the run by asking or stated inline (customer/system, capabilities preferences, or any other), write it back into the profile additively (keyed by the current repo's remote where system-specific) so future runs resolve without asking. Never write the token to the profile.
6. **Capabilities** — The Sigrid analyses to run (also known as "models" or "licenses"). Must be provided as a comma-separated string. Valid values: `maintainability`, `osh`, `security`. Example: `maintainability,osh`. No default. When unclear, ask the user which capabilities are needed.

## Running the analysis

`agents.py` prints feedback to stdout as one `Inline results: <capability>` line followed by one JSON line, per capability, interleaved with progress logging.

```bash
<PYTHON> "$SIGRIDCI_DIR/sigridci/agents.py" \
  --customer <CUSTOMER> \
  --system <SYSTEM> \
  --source <SOURCE_ROOT> \
  --capability <CAPABILITIES>
```

`<PYTHON>` is from the Python preflight check, `<SIGRIDCI_DIR>` from `ensure_sigridci.py`. The run blocks until analysis completes (up to ~30 minutes); read the JSON straight from the command's output.

There's no `--publish`/`--publishonly` support here — this skill is feedback-only. That also means on-boarding never occurs: if the run reports the system isn't on-boarded, that's expected, so report it and don't retry rather than treating it as a crash. If the user asks to publish results or show them on the dashboard, tell them this skill doesn't do that.

## Avoid

- **NEVER** print, echo, or log the `SIGRID_CI_TOKEN` or `SIGRID_TOKEN` value — this includes indirectly, via `env`, `printenv`, `env | grep ...`, `echo $SIGRID_CI_TOKEN`, or quoting it in a response to the user. If `agents.py` reports a token problem, relay its message; `check_token.py`'s presence/length output is the only thing worth inspecting on your own — tool results and your own responses both persist to the transcript, so "just debugging" leaks the token exactly as much as showing it to the user on purpose.
- **NEVER** guess customer or system names — always ask the user when unclear.
