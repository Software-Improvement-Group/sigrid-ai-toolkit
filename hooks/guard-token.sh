#!/usr/bin/env bash
#
# PreToolUse hook — blocks Bash commands that would leak SIGRID_TOKEN.
#
# Exit codes:
#   0 = allow the command
#   2 = block the command (stderr message shown to Claude as feedback)
#
# Receives JSON on stdin with shape:
#   { "tool_name": "Bash", "tool_input": { "command": "..." } }

set -euo pipefail

INPUT="$(cat)"
COMMAND="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"

# Nothing to check if command is empty
[ -z "$COMMAND" ] && exit 0

# ── Patterns that would expose the token value ──────────────────────────
BLOCKED_PATTERNS=(
  # Direct printing of the variable
  'echo[[:space:]].*SIGRID_TOKEN'
  'printf[[:space:]].*SIGRID_TOKEN'

  # Environment dumping commands
  '\bprintenv\b'
  '\benv\b[[:space:]]*$'
  '\benv\b[[:space:]]+[^=]'
  '\bset\b[[:space:]]*$'
  '\bexport\b[[:space:]]*-p'
  '\bdeclare\b[[:space:]]*-x'

  # Reading the variable into output
  'cat.*SIGRID_TOKEN'
  '\bless\b.*SIGRID_TOKEN'
  '\bmore\b.*SIGRID_TOKEN'

  # Curl/wget sending token to non-Sigrid domains
  'curl[[:space:]].*Bearer.*[^s]igrid'
  'wget[[:space:]].*Bearer.*[^s]igrid'

  # Logging token to a file
  '>.*SIGRID_TOKEN'
  'tee.*SIGRID_TOKEN'
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qE "$pattern"; then
    echo "BLOCKED: This command would expose SIGRID_TOKEN. Use '[ -n \"\$SIGRID_TOKEN\" ] && echo \"Token is set\"' to check existence without revealing the value." >&2
    exit 2
  fi
done

exit 0
