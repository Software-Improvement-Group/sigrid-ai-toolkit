#!/usr/bin/env bash
#
# PreToolUse hook — blocks Sigrid API calls when required environment
# variables are not set.
#
# Checks for: SIGRID_CI_TOKEN, SIGRID_CUSTOMER, SIGRID_SYSTEM
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

# Only check prerequisites for commands that call the Sigrid API
if ! echo "$COMMAND" | grep -q 'sigrid-says.com/rest'; then
  exit 0
fi

MISSING=()

if [ -z "${SIGRID_CI_TOKEN:-}" ]; then
  MISSING+=("SIGRID_CI_TOKEN  — your Sigrid API token (obtain from https://sigrid-says.com account settings)")
fi

if [ -z "${SIGRID_CUSTOMER:-}" ]; then
  MISSING+=("SIGRID_CUSTOMER  — your Sigrid account name")
fi

if [ -z "${SIGRID_SYSTEM:-}" ]; then
  MISSING+=("SIGRID_SYSTEM    — the system name as registered in Sigrid")
fi

if [ ${#MISSING[@]} -gt 0 ]; then
  {
    echo "BLOCKED: Missing required environment variables for Sigrid API calls:"
    echo ""
    for var in "${MISSING[@]}"; do
      echo "  - $var"
    done
    echo ""
    echo "Set them in your terminal before using Sigrid skills:"
    echo "  export SIGRID_CI_TOKEN=<your-token>"
    echo "  export SIGRID_CUSTOMER=<account-name>"
    echo "  export SIGRID_SYSTEM=<system-name>"
  } >&2
  exit 2
fi

exit 0
