#!/usr/bin/env bash
#
# PreToolUse hook — blocks any Bash command that references SIGRID_TOKEN.
#
# No legitimate command needs the token name on the command line.
# Scripts read it internally via os.environ; the agent should never
# reference, print, pass, or manipulate the variable directly.
#
# Exit codes:
#   0 = allow the command
#   2 = block the command (stderr message shown to the agent as feedback)
#
# Receives JSON on stdin with shape:
#   { "tool_name": "Bash", "tool_input": { "command": "..." } }

set -euo pipefail

INPUT="$(cat)"
COMMAND="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"

[ -z "$COMMAND" ] && exit 0

if echo "$COMMAND" | grep -q 'SIGRID_TOKEN'; then
  echo "BLOCKED: Commands must not reference SIGRID_TOKEN. Scripts read it from the environment automatically." >&2
  exit 2
fi

exit 0
