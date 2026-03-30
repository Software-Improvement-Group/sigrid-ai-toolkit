#!/usr/bin/env bash
#
# PreToolUse hook — blocks Sigrid API calls when SIGRID_CI_TOKEN is not set.
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

# Only check for commands that call the Sigrid API
if ! echo "$COMMAND" | grep -q 'sigrid-says.com/rest'; then
  exit 0
fi

if [ -z "${SIGRID_CI_TOKEN:-}" ]; then
  {
    echo "BLOCKED: SIGRID_CI_TOKEN is not set."
    echo ""
    echo "Set it in your terminal before using Sigrid skills:"
    echo "  export SIGRID_CI_TOKEN=<your-token>"
    echo ""
    echo "Obtain a token from https://sigrid-says.com account settings."
  } >&2
  exit 2
fi

exit 0
